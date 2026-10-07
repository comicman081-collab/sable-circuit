// Store physical key positions: Korean IME and Shift can change event.key.
const movementCodes=new Set(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowLeft','ArrowDown','ArrowRight']);
const controlCodes=new Set([...movementCodes,'ShiftLeft','ShiftRight','KeyR','Space']);
const keyAliases=new Map([
  ['w','KeyW'],['a','KeyA'],['s','KeyS'],['d','KeyD'],
  ['W','KeyW'],['A','KeyA'],['S','KeyS'],['D','KeyD'],
  // Korean IME may expose the text value instead of a useful code.
  ['ㅈ','KeyW'],['ㅁ','KeyA'],['ㄴ','KeyS'],['ㅇ','KeyD'],
  ['Shift','ShiftLeft'],['ShiftLeft','ShiftLeft'],['ShiftRight','ShiftRight'],
  ['r','KeyR'],['R','KeyR'],[' ','Space'],['Spacebar','Space'],
  ['ArrowUp','ArrowUp'],['ArrowLeft','ArrowLeft'],['ArrowDown','ArrowDown'],['ArrowRight','ArrowRight']
]);
export function physicalCode(event){
  const code=String(event?.code||'');
  if(controlCodes.has(code))return code;
  return keyAliases.get(String(event?.key||''))||code;
}

export function keyboardTargetConsumes(event){
  const target=event.target;
  if(!target)return false;
  if(target.isContentEditable||['TEXTAREA','SELECT'].includes(target.tagName))return true;
  if(target.tagName!=='INPUT')return false;
  const type=target.type||'text';
  if(!['range','checkbox','radio','button','submit','reset'].includes(type))return true;
  // Keep native keyboard operation of the focused slider/checkbox available.
  const code=physicalCode(event);
  return (type==='range'&&code.startsWith('Arrow'))||(['checkbox','radio'].includes(type)&&code==='Space');
}

export class CombatKeyboard {
  constructor(){this.codes=new Set();}
  clear(){this.codes.clear();}
  keyDown(event,{followMovement=true}={}){
    const code=physicalCode(event);
    if(!controlCodes.has(code)||keyboardTargetConsumes(event))return {handled:false};
    const first=!this.codes.has(code);
    this.codes.add(code);
    const movement=movementCodes.has(code);
    return {handled:true,movement,
      takeFacing:movement&&first&&followMovement,
      firePressed:first&&code==='Space',reloadPressed:first&&code==='KeyR'};
  }
  keyUp(event){this.codes.delete(physicalCode(event));}
  read(){
    const down=(a,b)=>this.codes.has(a)||this.codes.has(b);
    return {x:+down('KeyD','ArrowRight')-+down('KeyA','ArrowLeft'),
      y:+down('KeyS','ArrowDown')-+down('KeyW','ArrowUp'),
      run:down('ShiftLeft','ShiftRight'),fire:this.codes.has('Space'),reload:this.codes.has('KeyR')};
  }
}
