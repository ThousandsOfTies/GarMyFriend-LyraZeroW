'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const {loadHardware}=require('../sources/gar-my-friend/application/hardware.cjs');
const root=path.resolve(__dirname,'..');

test('Product binds one common application to simulated and physical Lyra Zero W GPIO/SPI',()=>{
  const python=process.env.PYTHON||(process.platform==='win32'?'python':'python3');
  const simulation=execFileSync(python,[path.join(root,'tools/product.py'),'hardware','--environment','simulation'],{encoding:'utf8'}).trim();
  const vm=loadHardware(simulation);
  const board=loadHardware(path.join(root,'hardware'));
  assert.deepEqual(vm.display,{spi:'/dev/spidev0.0',chip:'/dev/gpiochip0',dc:3,hz:1000000,reset:4});
  assert.deepEqual(vm.rotary,{chip:'/dev/gpiochip0',clock:5,data:6,switch:7,bias:'pull-up'});
  assert.deepEqual(board.display,{...vm.display,hz:8000000},'Physical SPI speed may differ from the simulated transfer timing');
  assert.deepEqual(board.rotary,{...vm.rotary,debounceUs:1000},'Only the physical profile requests kernel debounce');
});
