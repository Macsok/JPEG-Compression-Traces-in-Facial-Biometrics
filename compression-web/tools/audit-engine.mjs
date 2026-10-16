import * as A from './anatomy/audit.mjs';
import { columnSignal, spectrum } from '../app/static/engine-signal.mjs';

// Build-time only: ray-cast the rounded prisms in their actual SVG paint order.
// Surface engravings are checked separately by Anatomy's browser line check.
export function auditEngine(parts, projection) {
  const items=parts.map(({plan,z,height,steps,piece,move},index)=>({
    name:`${piece} (${plan.x},${plan.y},${z})`,
    // Keep DOM order fixed even as the audit poses a moving item.
    key:index*10000,
    piece,move,
    shapes:[A.slab(plan,z,height,{},steps)],
  }));
  const states=[];
  for(const detailed of [false,true]) {
    for(let step=0;step<=14;step++) {
      const position=step/2;
      const levels=spectrum(columnSignal(position,detailed));
      states.push({
        label:`${detailed?'detail':'smooth'} column ${position+1}`,
        shares:{bridge:position/7,...Object.fromEntries(levels.map((level,i)=>[`meter-${i}`,level]))},
      });
    }
  }
  // Include cursor extremes beyond the sample's current range. Opposite levels
  // on adjacent meters expose occlusion errors hidden by synchronized motion.
  for(const parity of [0,1]) states.push({
    label:`alternating cursor limits ${parity}`,
    shares:{bridge:parity,...Object.fromEntries(Array.from({length:8},(_,i)=>[`meter-${i}`,(i+parity)%2]))},
  });
  const result=A.depthOrder(items,projection,{states});
  if(result.missing.length||result.problems.length) {
    const pairs=new Set(result.problems.map(p=>`${p.front} must follow ${p.back}${p.cycle?' (interlocking shapes)':''}`));
    throw new Error(`Engine depth audit failed:\n${[...pairs,...result.missing].join('\n')}`);
  }
  console.log(`Engine depth audit passed: ${items.length} solids, ${states.length} poses, 0 incorrect overlaps`);
}
