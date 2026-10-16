import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as k from './anatomy/iso-kit.mjs';
import { samplePixel } from '../app/static/engine-signal.mjs';

// A physical assembly: all raised parts have a support, traces lie on the PCB.
const BASE = {x:-218,y:-176,w:436,d:352,r:12};
const PCB = {x:-203,y:-162,w:406,d:324,r:6};
const P = k.fitProjection([...k.boxCorners(BASE,-24,4), ...k.boxCorners({x:-178,y:-150,w:350,d:280,r:0},4,90)],1000,800,{pad:80,azimuth:43,elevation:38});
const S = k.solidSvg, L = k.lineSvg;
const at = p => k.iso(p,P);
const pieces=[];
let solids=0;
const slab=(x,y,w,d,z,h,tone='mid',r=1.5,extra={})=>{
  solids++;
  return S(k.slabOf({x,y,w,d,r},z,h,P,4,Math.min(.8,h/3)),{tone,...extra});
};
const groove=(x,y,w,d,z,tone='faint',r=1)=>L(k.planOutline({x,y,w,d,r},z,P,4),{tone});
const screw=(x,y,z,size=1.8)=>L(k.ring(x,y,size,z,P,16),{tone:'mid'})+k.dotsSvg([at([x,y,z])],{size:.55,tone:'hi'});
const bolts=(plan,z,inset=5)=>k.corners(plan,inset).map(([x,y])=>screw(x,y,z)).join('');
const byDepth=pts=>[...pts].sort((a,b)=>k.depthOf([...a,0],P)-k.depthOf([...b,0],P));
const group=(id,svg)=>`<g id="${id}">${svg}</g>`;

// Chassis, feet, gasket, lid and PCB standoffs.
pieces.push(`<path class="iso-halo" d="${k.haloOf(BASE,-24,14,P)}"/>`);
for(const [x,y] of byDepth(k.corners(BASE,26))) {
  pieces.push(slab(x-12,y-12,24,24,-24,5,'lo',4));
  pieces.push(slab(x-9,y-9,18,18,-19,5,'mid',2));
}
solids++;
pieces.push(S(k.slabOf(BASE,-14,12,P,8,1.4),{tone:'mid',inner:L(k.sideSeam(BASE,-8,P,8),{tone:'lo'})}));
pieces.push(slab(-216,-174,432,348,-2,2,'lo',11));
pieces.push(groove(-211,-169,422,338,0,'lo',8));
pieces.push(bolts(BASE,0,9));
for(const [x,y] of byDepth(k.corners(PCB,7))) pieces.push(slab(x-4,y-4,8,8,0,3,'mid'));
pieces.push(slab(PCB.x,PCB.y,PCB.w,PCB.d,3,1,'lo',PCB.r));
pieces.push(groove(-198,-157,396,314,4,'faint',4));
pieces.push(bolts(PCB,4,7));

// Etched tracks have plated terminals, never free ends or floating connectors.
const tracks=[], pulses=[];
function track(points, index, bank) {
  const projected=points.map(([x,y])=>at([x,y,4.12]));
  const d=k.pathOf(projected);
  const id=`engine-track-${bank}-${index}`;
  tracks.push(`<path id="${id}" class="iso-line engine-track" data-tone="lo" d="${d}"/>`);
  for(const [x,y] of [points[0],points[points.length-1]]) tracks.push(screw(x,y,4.12,1.4));
  pulses.push(`<circle class="engine-packet" data-track="${id}" data-phase="${index/8}" cx="${projected[0][0]}" cy="${projected[0][1]}" r="1.6" opacity="0"/>`);
}
for(let i=0;i<8;i++) {
  const sy=-88+i*11, dy=-33+i*10;
  track([[-31,sy],[-20,sy],[18,dy],[37,dy]],i,'input');
  const x=46+i*10, dest=-121+i*31;
  track([[x,54],[x,66],[dest,92],[dest,103]],i,'output');
}
for(let i=0;i<6;i++) track([[147,-78+i*16],[135,-78+i*16],[126,-67+i*17]],i,'power');
pieces.push(group('engine-traces',tracks.join('')+pulses.join('')));

// Back-edge memory sockets and upright circuit boards.
let memory='';
for(const x of [-180,-80]) {
  memory+=slab(x,-146,84,13,4,5,'lo');
  memory+=slab(x+4,-142,76,3,9,32,'mid',.6);
  for(let j=0;j<4;j++) {
    memory+=slab(x+9+j*16,-139,12,3,18,15,'mid',.6);
    // Contact fingers on the board's visible face are flat engravings.
    for(let n=0;n<3;n++) memory+=L(k.pathOf([[x+10+j*16+n*3,-138.9,11],[x+11.2+j*16+n*3,-138.9,11],[x+11.2+j*16+n*3,-138.9,16],[x+10+j*16+n*3,-138.9,16]].map(at),true),{tone:'lo'});
  }
  for(const end of [x,x+79]) memory+=slab(end,-146,5,13,9,8,'hi',.7);
  memory+=L(k.sideSeam({x:x+4,y:-142,w:76,d:3,r:.6},37,P,4),{tone:'lo'});
}
pieces.push(group('engine-memory',memory));

// Cooling assembly, each fin is its own solid and touches the spreader.
let cooling=slab(36,-146,94,63,4,5,'lo',3);
cooling+=slab(40,-142,86,55,9,5,'mid',2);
cooling+=screw(39,-143,9)+screw(127,-87,9);
for(let i=0;i<12;i++) cooling+=slab(42+i*7,-139,2.6,49,14,28,'mid',.5);
pieces.push(group('engine-cooling',cooling));

// Sensor cartridge. The bridge travels only along x and clears every neighbor.
let sensor='';
for(const y of [-112,26]) {
  sensor+=slab(-184,y-4,164,12,4,5,'lo');
  sensor+=slab(-179,y-1,154,6,9,5,'mid',.5);
  for(const x of [-185,-24]) sensor+=slab(x,y-4,5,12,9,11,'hi',.8)+screw(x+2.5,y+2,20,1.2);
}
sensor+=slab(-170,-99,134,117,4,4,'lo',3);
sensor+=slab(-165,-94,124,107,8,3,'hi',2);
for(let col=0;col<8;col++) {
  let cells='';
  for(let row=0;row<8;row++) {
    const shade=samplePixel(col,row);
    const d=k.planOutline({x:-161+col*14.6,y:-90+row*12.2,w:13.6,d:11.2,r:.6},11.12,P,3);
    cells+=`<path class="engine-pixel" data-pixel="${col},${row}" fill="rgb(${shade},${shade},${shade})" d="${d}"/>`;
  }
  sensor+=`<g data-engine-column="${col}">${cells}</g>`;
}
sensor+=slab(-174,44,139,6,4,.7,'lo',.7);
const scale=k.topTicks(-170,-38,4,4,44,4.7,[2,4],P);
sensor+=L(scale.minor,{tone:'lo'})+L(scale.major,{tone:'mid'});
pieces.push(group('engine-sensor',sensor));
const reticle=groove(-161,-90,13.6,96.6,11.2,'hi',.6);
pieces.push(group('engine-reticle',reticle));

// A real inset scope. The trace lies in the glass plane, clipped to the bezel.
let scope=slab(-201,-106,15,132,4,3,'lo',2);
scope+=slab(-200,-105,13,130,7,2,'mid',1.5);
scope+=slab(-199,-100,11,120,9,.5,'lo',.8);
scope+=bolts({x:-200,y:-105,w:13,d:130},9,2);
const scopePlane=k.topMatrix([-199,19],9.6,P,'y');
scope+=`<g transform="${scopePlane}"><defs><clipPath id="engine-scope-clip"><rect x="0" y="0" width="118" height="10" rx=".5"/></clipPath></defs><g clip-path="url(#engine-scope-clip)"><rect class="engine-scope-glass" width="118" height="10"/>`;
for(let i=1;i<8;i++) scope+=`<path class="iso-line engine-scope-grid" d="M${i*118/8} 0V10"/>`;
scope+=`<path class="iso-line engine-scope-grid" d="M0 5H118"/><path id="engine-scope-trace" class="iso-line engine-scope-trace" d="M2 5H116"/>`;
for(let i=0;i<8;i++) scope+=`<circle data-scope-point="${i}" class="engine-scope-point" cx="${2+i*114/7}" cy="5" r=".65"/>`;
scope+='</g></g>';
pieces.push(group('engine-scope',scope));

// Power-stage packages on the right edge, seated on ceramic pads.
let power='';
for(let i=0;i<5;i++) {
  power+=slab(153,-96+i*30,32,24,4,2,'lo',1.2);
  power+=slab(157,-92+i*30,24,16,6,10,'mid',1.5);
  power+=groove(160,-89+i*30,18,10,16,'lo');
  power+=screw(156,-94+i*30,6,1);
}
for(let i=0;i<4;i++) power+=slab(140,-139+i*12,11,8,4,7,'hi',1);
pieces.push(group('engine-power',power));

// Exposed processor package and a small, truly planar die pattern.
let core=slab(31,-50,100,108,4,4,'lo',4);
for(let i=0;i<8;i++) {
  core+=slab(27,-40+i*11,4,6,4,1,'lo',.3);
  core+=slab(131,-40+i*11,4,6,4,1,'lo',.3);
}
core+=slab(39,-42,84,92,8,6,'mid',3);
core+=slab(47,-34,68,76,14,2,'hi',1.6);
core+=slab(53,-28,56,64,16,2,'hi',1.2,{lit:true});
for(let i=0;i<8;i++) {
  let row='';
  for(let j=0;j<8;j++) row+=groove(56+i*6.3,-25+j*7.2,4.8,5.6,18,'lo',.3);
  core+=`<g data-engine-die="${i}">${row}</g>`;
}
for(const [x,y] of [[31,-42],[123,-42],[31,39],[123,39]]) core+=slab(x,y,8,11,8,9,'mid',1)+screw(x+4,y+5.5,17);
pieces.push(group('engine-core',core));

// Output daughterboard, a bank of eight independently lit channel windows.
let output='';
for(const [x,y] of byDepth([[-142,99],[133,99],[-142,143],[133,143]])) output+=slab(x-3,y-3,6,6,4,6,'lo');
output+=slab(-148,94,287,55,10,2,'mid',3);
output+=bolts({x:-148,y:94,w:287,d:55},12,5);
for(let i=0;i<8;i++) {
  const x=-132+i*31;
  output+=slab(x,105,24,33,12,7,'mid',1.5);
  output+=slab(x,105,24,7,19,42,'mid',1);
  output+=`<g transform="${k.sideMatrix([x,112.05],0,P,'left')}"><rect class="engine-meter-track" x="7" y="-55" width="10" height="33" rx="1"/>`;
  for(let tick=0;tick<6;tick++) output+=`<rect class="engine-meter-tick" x="3" y="${-27-tick*5}" width="3" height=".65"/>`;
  output+=`<rect data-spectrum-fill="${i}" class="engine-meter-fill" x="10" y="-24" width="4" height="1" rx=".5"/>`;
  for(const sx of [3,21]) output+=`<circle class="engine-meter-screw" cx="${sx}" cy="-58" r="1.1"/><circle class="engine-scope-point" cx="${sx}" cy="-58" r=".25"/>`;
  output+='</g>';
  output+=`<g data-spectrum-cursor="${i}">${slab(x+5,112,14,2.4,23,3,'hi',.4,{lit:true})}</g>`;
  output+=slab(x+3,122,18,11,19,.8,'lo',1);
  output+=`<path class="engine-window" data-engine-output="${i}" d="${k.planOutline({x:x+5,y:124,w:14,d:7,r:1},19.9,P,4)}"/>`;
  output+=screw(x+12,136,19,1);
}
pieces.push(group('engine-output',output));

// Enclosure edge: vent perforations and two real connector mouths.
let edge='';
for(let i=0;i<12;i++) edge+=groove(-190+i*8,155,4,5,4,'lo',1);
for(const x of [-46,45]) {
  edge+=slab(x,151,65,13,4,11,'mid',2);
  edge+=L(k.pathOf([[x+4,164.1,7],[x+61,164.1,7],[x+61,164.1,12],[x+4,164.1,12]].map(at),true),{tone:'hi'});
  for(let i=0;i<8;i++) edge+=L(k.pathOf([[x+8+i*6,164.2,8],[x+10+i*6,164.2,8],[x+10+i*6,164.2,10],[x+8+i*6,164.2,10]].map(at),true),{tone:'lo'});
  edge+=screw(x+4,156,15,1.1)+screw(x+61,156,15,1.1);
}
edge+=slab(150,110,35,32,4,.8,'lo');
edge+=k.faceTextSvg(k.topMatrix([153,123],4.8,P),'CI / 02',{size:3.8,tone:'mid'});
edge+=groove(153,129,26,5,4.8,'lo',.4);
pieces.push(group('engine-edge',edge));

// Moving assembly, built once. No per-frame geometry or large DOM rebuild.
let bridge='';
for(const y of [-112,26]) {
  bridge+=slab(-166,y-4,16,12,14,6,'mid',1);
  bridge+=slab(-163,y-1,10,6,20,53,'mid',.7);
  bridge+=slab(-166,y-4,16,12,69,4,'hi',1);
  bridge+=screw(-158,y+2,73,1.5);
}
bridge+=slab(-166,-116,16,154,73,9,'hi',1.8);
bridge+=groove(-162,-112,8,146,82,'lo');
bridge+=slab(-173,-56,30,36,60,13,'mid',2);
bridge+=slab(-170,-53,24,30,58,2,'hi',1,{lit:true});
bridge+=slab(-171,-54,26,32,82,3,'hi',1.5);
for(let i=0;i<5;i++) bridge+=groove(-167,-49+i*4.4,18,1.8,85,'lo',.7);
bridge+=screw(-168,-51,85,1.2)+screw(-148,-25,85,1.2);
const vector=k.axisVector(P,[1,0,0]);
pieces.push(`<g id="engine-bridge" data-vector="${vector.join(',')}" data-travel="102.2">${bridge}</g>`);

const svg=`<!-- Generated by tools/build-engine.mjs. ${solids} structural solids; surface inlays are separate. -->
<svg id="engine-svg" class="iso-svg" data-lift-vector="${k.axisVector(P,[0,0,1]).join(',')}" viewBox="0 0 1000 800" aria-hidden="true" focusable="false">
<g id="engine-camera">${pieces.join('\n')}</g>
</svg>\n`;
writeFileSync(fileURLToPath(new URL('../app/templates/engine.svg',import.meta.url)),svg);
console.log(`Built engine: ${solids} solids, ${(svg.length/1024).toFixed(1)} KiB`);
