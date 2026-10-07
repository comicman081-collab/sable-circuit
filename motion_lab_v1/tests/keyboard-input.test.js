import test from 'node:test';
import assert from 'node:assert/strict';
import {CombatKeyboard,keyboardTargetConsumes} from '../public/keyboard-input.js';
import {Actor,STEP,DIRECTIONS} from '../public/simulation.js';

const profile={radius:.19,locomotion:{walkSpeed:1.35,runSpeed:2.8,walkStride:1.6,runStride:1.95},weapon:{magazine:24,fireInterval:.11,reloadSeconds:1.25,damage:25}};
const layouts=[{KeyW:'w',KeyA:'a',KeyS:'s',KeyD:'d'},
  {KeyW:'ㅈ',KeyA:'ㅁ',KeyS:'ㄴ',KeyD:'ㅇ'},
  {KeyW:'W',KeyA:'A',KeyS:'S',KeyD:'D'},
  {KeyW:'Process',KeyA:'Process',KeyS:'Process',KeyD:'Process'}];
const diagonals=[['NW','KeyW','KeyA'],['NE','KeyW','KeyD'],['SW','KeyS','KeyA'],['SE','KeyS','KeyD']];

test('All four WASD diagonals work in either press order, with Korean/English/Shift/IME event values',()=>{
  for(const layout of layouts)for(const [facing,...codes]of diagonals)for(const order of [codes,[...codes].reverse()]){
    const keyboard=new CombatKeyboard(),actor=new Actor(profile);
    for(const code of order){keyboard.keyDown({code,key:layout[code]});actor.update(STEP,keyboard.read());}
    assert.equal(DIRECTIONS[actor.direction],facing,'Turn on the same physics step as the second key');
    for(let i=0;i<24;i++)actor.update(STEP,keyboard.read());
    assert.equal(Math.sign(actor.x),facing.endsWith('W')?-1:1);
    assert.equal(Math.sign(actor.y),facing.startsWith('N')?-1:1);
    assert.ok(actor.phase>0);
    // IME or Shift may change key text between keydown and keyup.
    for(const code of codes)keyboard.keyUp({code,key:'Unidentified'});
    assert.deepEqual(keyboard.read(),{x:0,y:0,run:false,fire:false,reload:false});
  }
});

test('Arrow key pairs drive all four diagonals through the same actor',()=>{
  for(const [facing,vertical,horizontal]of [['NW','ArrowUp','ArrowLeft'],['NE','ArrowUp','ArrowRight'],['SW','ArrowDown','ArrowLeft'],['SE','ArrowDown','ArrowRight']]){
    const keyboard=new CombatKeyboard(),actor=new Actor(profile);
    keyboard.keyDown({code:vertical});keyboard.keyDown({code:horizontal});actor.update(STEP,keyboard.read());
    assert.equal(DIRECTIONS[actor.direction],facing);
  }
});

test('Releasing one key returns to the remaining direction; opposite-key and alias chords do not stick',()=>{
  const keyboard=new CombatKeyboard(),actor=new Actor(profile);
  keyboard.keyDown({code:'KeyW'});keyboard.keyDown({code:'KeyD'});actor.update(STEP,keyboard.read());
  assert.equal(DIRECTIONS[actor.direction],'NE');
  keyboard.keyUp({code:'KeyD'});actor.update(STEP,keyboard.read());assert.equal(DIRECTIONS[actor.direction],'N');
  keyboard.keyDown({code:'ArrowUp'});keyboard.keyUp({code:'KeyW'});assert.equal(keyboard.read().y,-1);
  keyboard.keyDown({code:'KeyS'});assert.equal(keyboard.read().y,0);
  keyboard.keyUp({code:'ArrowUp'});actor.update(STEP,keyboard.read());assert.equal(DIRECTIONS[actor.direction],'S');
  keyboard.clear();assert.equal(keyboard.read().y,0);
});

test('A new movement chord takes facing from an idle pointer, but key repeat does not cancel active mouse aim',()=>{
  const keyboard=new CombatKeyboard();
  assert.equal(keyboard.keyDown({code:'KeyW'}).takeFacing,true);
  assert.equal(keyboard.keyDown({code:'KeyW',repeat:true}).takeFacing,false);
  assert.equal(keyboard.keyDown({code:'KeyA'}).takeFacing,true);
  keyboard.clear();
  assert.equal(keyboard.keyDown({code:'KeyW'},{mouseAiming:true}).takeFacing,true,'Held fire cannot lock out a fresh movement direction');
  assert.equal(keyboard.keyDown({code:'KeyA'},{followMovement:false}).takeFacing,false);
});

test('Shift and Space continue to work with diagonal motion and independent mouse firing',()=>{
  const keyboard=new CombatKeyboard(),actor=new Actor(profile);
  keyboard.keyDown({code:'KeyW',key:'ㅈ'});keyboard.keyDown({code:'KeyD',key:'ㅇ'});
  keyboard.keyDown({code:'ShiftLeft'});keyboard.keyDown({code:'ShiftRight'});keyboard.keyDown({code:'Space'});
  keyboard.keyUp({code:'ShiftLeft'});
  for(let i=0;i<24;i++)actor.update(STEP,{...keyboard.read(),aim:Math.PI});
  assert.equal(actor.run,true);assert.equal(DIRECTIONS[actor.direction],'W');assert.ok(actor.x>0&&actor.y<0&&actor.shots>0);
  keyboard.keyUp({code:'Space'});keyboard.keyUp({code:'ShiftRight'});assert.equal(keyboard.read().run,false);assert.equal(keyboard.read().fire,false);
});

test('Settings controls allow WASD without swallowing text editing or native slider/checkbox keys',()=>{
  for(const type of ['range','checkbox','radio']){
    const keyboard=new CombatKeyboard();
    assert.equal(keyboard.keyDown({code:'KeyW',target:{tagName:'INPUT',type}}).handled,true);
    assert.equal(keyboard.read().y,-1);
  }
  assert.equal(keyboardTargetConsumes({code:'ArrowUp',target:{tagName:'INPUT',type:'range'}}),true);
  assert.equal(keyboardTargetConsumes({code:'Space',target:{tagName:'INPUT',type:'checkbox'}}),true);
  for(const target of [{tagName:'INPUT',type:'text'},{tagName:'TEXTAREA'},{tagName:'DIV',isContentEditable:true}]){
    assert.equal(new CombatKeyboard().keyDown({code:'KeyW',target}).handled,false);
  }
});

test('Keyboard movement, reload, and fire all clear on focus loss',()=>{
  const keyboard=new CombatKeyboard();
  for(const code of ['KeyW','KeyA','Space','ShiftLeft','KeyR'])keyboard.keyDown({code});
  keyboard.clear();assert.deepEqual(keyboard.read(),{x:0,y:0,run:false,fire:false,reload:false});
});
