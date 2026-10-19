'use strict';
// One-shot flattening of generated donor silhouettes; preserves ancestral pixels.
const fs = require('node:fs'), crypto = require('node:crypto');
const {decodePNG, encodePNG, preview} = require('./finish_wall.js');
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const source = 'artifacts/line-1/wall-v14.png';
const destination = 'artifacts/line-1/wall-v15.png';
const ancestor = decodePNG(source), donor = decodePNG(destination);
const prior = JSON.parse(fs.readFileSync('dist/line-1/32.json', 'utf8'));
if (prior.image !== 'https://api.imd.fun/artifacts/' + hash(fs.readFileSync(source))) throw Error('ancestor digest mismatch');
if (ancestor.width !== 1254 || ancestor.height !== 1254 || ancestor.channels !== 3 || donor.width !== 1024 || donor.height !== 1024) throw Error('unexpected input dimensions; refuses rerun on finished output');
const out = {...ancestor, pixels: Buffer.from(ancestor.pixels)};
const bounds = [825, 940, 993, 1040];
function dab(x,y,color,alpha) {
  if(x<bounds[0]||x>=bounds[2]||y<bounds[1]||y>=bounds[3]) throw Error('paint outside bounded patch');
  const i=(y*out.width+x)*3;
  for(let c=0;c<3;c++) out.pixels[i+c]=Math.round(out.pixels[i+c]*(1-alpha)+color[c]*alpha);
}
// Flatten the first generated twig and its stone silhouettes into two narrow
// rubbings, reversing the pigments in the second. Donor brightness affects
// only sparse wear; no object shading or generated rock is transferred.
const donorBox=[416,757,594,827], scale=.72;
for(let row=0;row<2;row++) {
  const left=842+row*17, top=948+row*43;
  for(let y=0;y<Math.ceil((donorBox[3]-donorBox[1])*scale);y++) {
    for(let x=0;x<Math.ceil((donorBox[2]-donorBox[0])*scale);x++) {
      const sx=donorBox[0]+x/scale, sy=donorBox[1]+y/scale;
      const red=Math.hypot((sx-438)/20,(sy-797)/21);
      const chalk=Math.hypot((sx-563)/21,(sy-782)/18);
      const t=(sx-438)/(583-438), lineY=810+(799-810)*t;
      const twig=t>=0&&t<=1&&Math.abs(sy-lineY)<5.5;
      const noise=(Math.sin((sx+row*13)*12.9898+sy*78.233)*43758.5453)%1;
      const at=(Math.min(donor.height-1,Math.floor(sy))*donor.width+Math.min(donor.width-1,Math.floor(sx)))*donor.channels;
      const lum=(donor.pixels[at]+donor.pixels[at+1]+donor.pixels[at+2])/3;
      // Jagged silhouette edges and pinholes expose the exact underlying rock.
      if(noise<-.67 || (lum<50 && noise<-.28)) continue;
      let color, alpha;
      if(red<.94+noise*.05) { color=row?[202,177,128]:[139,53,27]; alpha=.69; }
      else if(chalk<.94+noise*.05) { color=row?[139,53,27]:[202,177,128]; alpha=.69; }
      else if(twig) { color=[42,30,22]; alpha=.68; }
      else continue;
      dab(left+x,top+y,color,alpha+(noise*.11));
    }
  }
}
let changed=0;
for(let y=0;y<out.height;y++) for(let x=0;x<out.width;x++) {
  const i=(y*out.width+x)*3;
  if(!out.pixels.subarray(i,i+3).equals(ancestor.pixels.subarray(i,i+3))) {
    changed++;
    if(x<bounds[0]||x>=bounds[2]||y<bounds[1]||y>=bounds[3]) throw Error('ancestral pixels changed outside patch');
  }
}
if(changed<500) throw Error('new mark missing');
const png=encodePNG(out), jpg=preview(out), digest=hash(png);
if(jpg.length>100000) throw Error('JPEG exceeds 100 KB');
const record={name:'The Swapped Weights',image:'https://api.imd.fun/artifacts/'+digest,attributes:[
  {trait_type:'Cave',value:'Roots'}, {trait_type:'Wall',value:'Line 1'},
  {trait_type:'Number',value:33}, {trait_type:'Left behind',value:'Metric Verdict'},
  {trait_type:'Meaning',value:'Two paired weights trade sides to ask how often chance could tip the balance.'},
  {trait_type:'One thing',value:'Reproducible benchmark evidence'}
]};
if(fs.existsSync('dist/line-1/33.json')) throw Error('record already exists');
fs.writeFileSync(destination,png);
fs.writeFileSync('artifacts/line-1/wall.png',png);
fs.writeFileSync('dist/line-1/33.jpg',jpg);
fs.writeFileSync('dist/line-1/33.json',JSON.stringify(record,null,2)+'\n');
const review={wall:destination,width:out.width,height:out.height,format:'PNG RGB8',bytes:png.length,sha256:digest,
 preview:{path:'dist/line-1/33.jpg',width:512,height:512,format:'JPEG',bytes:jpg.length},
 ancestor:'artifacts/line-1/wall-v14.png',ancestor_sha256:hash(fs.readFileSync(source)),bounds,changed_pixels:changed,
 all_pixels_outside_bounds_identical:true,
 process:'Installed native image edit generated donor silhouettes. Flattened them into textured earth-pigment rubbings on the exact inherited wall; discarded all generated background and object shading. Generated intermediate overwritten by final wall.',
 visual_review:{pepe_wide_mouth_and_heavy_lidded_eyes_preserved:true,ancestral_hands_concealed:true,new_hands_or_stencils:0,visible_digits_to_count:0,prohibited_text_observed:false,unmet_visual_requirements:[]},
 limitations:['Local visual review only; no independent visual approval.','Fine wear is less distinct in the 512-pixel preview.'],
 preview_location:'Required numbered JPEG beside the record, as explicitly specified by FILES; no other new pictures outside artifacts.'};
fs.writeFileSync('line-1/wall-review-33.json',JSON.stringify(review,null,2)+'\n');
console.log(JSON.stringify(review));
