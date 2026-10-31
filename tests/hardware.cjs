'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {loadHardware}=require('../sources/gar-my-friend/application/hardware.cjs');
const root=path.resolve(__dirname,'..');

test('Product binds one common application to simulated and physical Lyra Zero W GPIO/SPI',()=>{
  const vm=loadHardware(path.join(root,'hardware'));
  const board=loadHardware(path.join(root,'hardware/lyra-zero-w'));
  assert.deepEqual(vm.display,{spi:'/dev/spidev0.0',chip:'/dev/gpiochip0',dc:3,hz:1000000,reset:4});
  assert.deepEqual(vm.rotary,{chip:'/dev/gpiochip0',clock:5,data:6,switch:7,bias:'pull-up'});
  assert.deepEqual(board.display,{...vm.display,hz:8000000},'Physical SPI speed may differ from the simulated transfer timing');
  assert.deepEqual(board.rotary,{...vm.rotary,debounceUs:1000},'Only the physical profile requests kernel debounce');
});
