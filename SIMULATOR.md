# Lyra Zero W版のLinuxシミュレータ

## 構成

- Product: `GarMyFriend-LyraZeroW`
- VM: `gar-myfriend-lyra-zero-w-sim`（x86_64 Ubuntu、1 CPU、1GB）
- SSH: `127.0.0.1:2232`
- WebPanel: `http://127.0.0.1:8774`
- VM内の配置: `/home/gar/GarMyFriend-LyraZeroW`
- 状態・鍵・ログ: `.gar/vm/`（Git対象外）

`config/simulator.json`がVM名・ポート・メモリーの設定です。
VM内では`garmyfriend-lyra-zero-w`、`garmyfriend-lyra-zero-w-devices`、
`garmyfriend-lyra-zero-w-panel`がそれぞれ顔アプリ、仮想デバイス、WebPanelを動かします。
ホスト側は専用SSHポートを使って、VM内のPanelへローカル転送します。

## 初回のVM作成

WindowsのVirtualBox、Git、Node.js 18以上、Python 3.11以上を使います。
検証済みのUbuntu 24.04 x86_64クラウドイメージ（VMDK）を用意し、
入手元で照合したSHA256を指定します。コピー先のVDIは専用VMのものとして新規作成します。

```powershell
python -m pip install pycdlib==1.22.0
python infra/virtualbox/create.py --base-image <VMDKのパス> --sha256 <照合済みSHA256>
npm ci
npm run sim
```

初回はLinuxパッケージとgpio-simのカーネルモジュールを導入するため時間がかかります。
VMが作成済みなら、再作成せず`npm run sim`で再開します。
このホストでは1 CPUで起動確認します。CPU数は実ボードのコア数の再現ではありません。

## 日常の操作

```powershell
npm run sim
npm run sim:open
npm run sim:status
npm run sim:deploy
npm run sim:stop
```

ブラウザーで`http://127.0.0.1:8774`を開くと、液晶とノブだけが表示されます。
＋／−、矢印キーで回転を入力でき、ノブまたはPRESSで押下できます。
フォーカス中のノブにはホイール入力も使えます。

SSHで調べる場合:

```powershell
ssh -i .gar/vm/id_ed25519 -p 2232 -o IdentitiesOnly=yes -o UserKnownHostsFile=.gar/vm/known_hosts gar@127.0.0.1
```

VM内の状態:

```sh
systemctl status garmyfriend-lyra-zero-w garmyfriend-lyra-zero-w-devices garmyfriend-lyra-zero-w-panel
journalctl -u garmyfriend-lyra-zero-w -n 30 --no-pager
```

## 確認

```powershell
npm test                  # 共通アプリ・CSV・Productのブラウザー接続
npm run test:shared       # gar-toolsの部品単体・複数インスタンス
npm run test:parts        # 本物の仮想GPIO/SPI、アプリとPanelの独立性
npm run test:vm           # 起動中のPanel操作とSPI画素の一致
```

`tests/vm-parts.py`は顔アプリを一時停止してもBridgeが顔を作らないこと、
Panel停止中も顔アプリがGPIOを読みSPIへ書くことを確認し、最後にPanelを復帰します。
`tests/vm-panel.cjs`はノブの回転・押下と、表示canvasが仮想SPIドライバの画素と
一致することを確認します。画像は`artifacts/vm-webpanel.png`に保存します。

VMの1MHz指定はSPI設定の互換性を確認する値です。CUSEは転送の電気的な所要時間を
再現しません。表示fpsや消費メモリーをRK3506実機の測定値として扱いません。
