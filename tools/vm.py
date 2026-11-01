"""Product-owned, isolated Linux simulation lifecycle. No physical-board access."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tarfile
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config/simulator.json').read_text(encoding='utf-8'))
STATE = ROOT / '.gar/vm'
NAME = CONFIG['vmName']
PRODUCT = CONFIG['product']
PORT = CONFIG['panelPort']
REMOTE = '/home/gar/' + PRODUCT
SERVICE = 'garmyfriend-lyra-zero-w'
URL = f'http://127.0.0.1:{PORT}'
VBOX = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Oracle/VirtualBox/VBoxManage.exe'
OPTIONS = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=7', '-o', 'IdentitiesOnly=yes',
           '-o', 'StrictHostKeyChecking=accept-new', '-o', f'UserKnownHostsFile={STATE / "known_hosts"}']
SSH = ['ssh', '-i', str(STATE / 'id_ed25519'), '-p', str(CONFIG['sshPort']), *OPTIONS, 'gar@127.0.0.1']


def run(args, *, capture=False, check=True, timeout=None):
    return subprocess.run(list(map(str, args)), cwd=ROOT, check=check, text=True,
                          encoding='utf-8', errors='replace', capture_output=capture, timeout=timeout)


def ssh(command, *, capture=False, check=True, timeout=None):
    return run([*SSH, command], capture=capture, check=check, timeout=timeout)


def vm_info():
    state = json.loads((STATE / 'vm.json').read_text(encoding='utf-8'))
    if state.get('name') != NAME or state.get('product') != PRODUCT or state.get('sshPort') != CONFIG['sshPort']:
        raise RuntimeError('VM identity does not match this Product; refusing to operate another VM')
    return run([VBOX, 'showvminfo', NAME, '--machinereadable'], capture=True).stdout


def start():
    if 'VMState="running"' not in vm_info():
        run([VBOX, 'startvm', NAME, '--type', 'headless'])
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        try:
            result = ssh('true', capture=True, check=False, timeout=10)
        except subprocess.TimeoutExpired:
            continue
        if result.returncode == 0:
            return
        time.sleep(2)
    raise RuntimeError('Dedicated VM SSH did not become ready')


def scp(source, destination):
    run(['scp', '-i', STATE / 'id_ed25519', '-P', CONFIG['sshPort'], *OPTIONS,
         source, 'gar@127.0.0.1:' + destination])


def archive():
    sys.path.insert(0, str(ROOT / 'sources/gar-tools/composition'))
    from product import Product
    profile = Product(ROOT).validate().hardware_for('simulation')
    generated = [(profile / name).relative_to(ROOT).as_posix() for name in ('gpio.csv', 'spi.csv')]
    STATE.mkdir(parents=True, exist_ok=True)
    # Include the pinned files directly; never copy a shared implementation into Product code.
    items = ['sources/gar-my-friend/application', 'sources/gar-my-friend/firmware',
             'sources/gar-my-friend/shared/expressions.json', 'sources/gar-my-friend/tools/build-native.sh',
             'scripts/run-face.cjs', 'simulation', 'simulator', 'hardware/gpio.csv', 'hardware/spi.csv',
             'hardware/components.csv', 'hardware/connections.csv', 'hardware/simulation-overrides.csv', 'product.json', 'infra/virtualbox',
             'tests/vm-parts.py', 'config/simulator.json']
    items += generated
    runtime = 'sources/gar-tools/targets/linux-device/runtime/'
    items += [runtime + part for part in ['gc9a01-output', 'gc9a01-stub', 'ili9341-stub', 'rotary-input', 'web-bridge']]
    items += ['sources/gar-tools/web-simulator/components/' + part for part in ['display.mjs', 'framebuffer.mjs', 'rotary.mjs']]

    def keep(info):
        if any(part in {'.git', '__pycache__', 'node_modules'} for part in Path(info.name).parts):
            return None
        if info.issym() or info.islnk():
            raise ValueError('Symlinks are not simulation deployment inputs')
        info.mode = 0o755 if info.isdir() else 0o644
        info.uid = info.gid = 0
        info.uname = info.gname = ''
        return info

    output = STATE / 'product.tar.gz'
    with tarfile.open(output, 'w:gz') as tar:
        for item in items:
            tar.add(ROOT / item, arcname=item, filter=keep)
    return output


def deploy():
    start()
    # The dedicated VM's first boot installs the kernel GPIO simulator and native build dependencies.
    ssh('cloud-init status --wait', timeout=900)
    scp(archive(), 'lyra-zero-w-product.tar.gz')
    ssh(f'mkdir -p {REMOTE} && tar -xzf /home/gar/lyra-zero-w-product.tar.gz -C {REMOTE} && sh {REMOTE}/infra/virtualbox/install.sh', timeout=180)


def health():
    with urllib.request.urlopen(URL + '/health', timeout=4) as response:
        value = json.load(response)
    if value.get('product') != PRODUCT or value.get('host', {}).get('environment') != 'virtualbox-linux':
        raise RuntimeError('Local port belongs to a different simulator')
    return value


def forward():
    with socket.socket() as probe:
        occupied = probe.connect_ex(('127.0.0.1', PORT)) == 0
    STATE.mkdir(parents=True, exist_ok=True)
    if not occupied:
        with (STATE / 'forward.log').open('ab') as log:
            command = [*SSH[:-1], '-o', 'ExitOnForwardFailure=yes', '-o', 'ServerAliveInterval=15',
                       '-o', 'ServerAliveCountMax=3', '-N', '-L', f'127.0.0.1:{PORT}:127.0.0.1:{PORT}', SSH[-1]]
            process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                       start_new_session=os.name != 'nt')
            (STATE / 'forward.json').write_text(json.dumps({'pid': process.pid, 'url': URL, 'vm': NAME}) + '\n')
    deadline = time.monotonic() + 30
    error = None
    while time.monotonic() < deadline:
        try:
            value = health()
            if value.get('ok'):
                (STATE / 'panel.json').write_text(json.dumps({'url': URL, 'vm': NAME, 'health': value}, indent=2) + '\n')
                return value
        except (OSError, ValueError) as exc:
            error = exc
        time.sleep(.3)
    raise RuntimeError('Local simulator did not become ready: ' + str(error))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['up', 'start', 'stop', 'status', 'deploy', 'open', 'test'])
    args = parser.parse_args()
    if args.command == 'up':
        deploy()
        forward()
        print(URL)
    elif args.command == 'deploy':
        deploy()
        forward()
        print(URL)
    elif args.command == 'start':
        start()
        forward()
        print(URL)
    elif args.command == 'stop':
        vm_info()
        run([VBOX, 'controlvm', NAME, 'acpipowerbutton'])
    elif args.command == 'open':
        start()
        forward()
        webbrowser.open(URL)
        print(URL)
    elif args.command == 'test':
        start()
        ssh(f'cd {REMOTE} && python3 -B tests/vm-parts.py', timeout=90)
    else:
        info = vm_info()
        print('\n'.join(line for line in info.splitlines() if line.startswith(('VMState=', 'memory=', 'cpus='))))
        if 'VMState="running"' in info:
            ssh(f'systemctl is-active {SERVICE} {SERVICE}-panel {SERVICE}-devices; curl -fsS http://127.0.0.1:{PORT}/health')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error))
