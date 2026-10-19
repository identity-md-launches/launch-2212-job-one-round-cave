// Preserve every ancestral pixel except pigment from the generated new motif.
// Node built-ins only; reads/writes only the explicitly named workspace images.
const fs = require('fs');
const zlib = require('zlib');
const crypto = require('crypto');
function decode(data) {
  let pos=8, idat=[], width,height;
  while(pos<data.length){let n=data.readUInt32BE(pos), kind=data.toString('ascii',pos+4,pos+8), p=data.subarray(pos+8,pos+8+n);
    if(kind==='IHDR'){width=p.readUInt32BE(0);height=p.readUInt32BE(4);if(p[8]!==8||p[9]!==2||p[12]!==0)throw Error('RGB8 noninterlaced required');}
    if(kind==='IDAT')idat.push(p);pos+=n+12;}
  let raw=zlib.inflateSync(Buffer.concat(idat)), stride=width*3, pixels=Buffer.alloc(width*height*3);
  if(raw.length!==(stride+1)*height)throw Error('scanline size');
  for(let y=0;y<height;y++){let mode=raw[y*(stride+1)];for(let x=0;x<stride;x++){
    let k=y*stride+x,a=x>=3?pixels[k-3]:0,b=y?pixels[k-stride]:0,c=y&&x>=3?pixels[k-stride-3]:0,p=0;
    if(mode===1)p=a;else if(mode===2)p=b;else if(mode===3)p=Math.floor((a+b)/2);else if(mode===4){let v=a+b-c, da=Math.abs(v-a),db=Math.abs(v-b),dc=Math.abs(v-c);p=da<=db&&da<=dc?a:db<=dc?b:c;}else if(mode!==0)throw Error('filter');
    pixels[k]=(raw[y*(stride+1)+1+x]+p)&255;}}
  return {width,height,pixels};
}
function crc(data){let c=0xffffffff;for(let b of data){c^=b;for(let j=0;j<8;j++)c=(c>>>1)^((c&1)?0xedb88320:0);}return (c^0xffffffff)>>>0;}
function chunk(name,data){let kind=Buffer.from(name),out=Buffer.alloc(data.length+12);out.writeUInt32BE(data.length,0);kind.copy(out,4);data.copy(out,8);out.writeUInt32BE(crc(Buffer.concat([kind,data])),data.length+8);return out;}
function encode(img){let header=Buffer.alloc(13);header.writeUInt32BE(img.width,0);header.writeUInt32BE(img.height,4);header[8]=8;header[9]=2;
 let stride=img.width*3,raw=Buffer.alloc((stride+1)*img.height);for(let y=0;y<img.height;y++)img.pixels.copy(raw,y*(stride+1)+1,y*stride,(y+1)*stride);
 return Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',header),chunk('IDAT',zlib.deflateSync(raw)),chunk('IEND',Buffer.alloc(0))]);}
const ancestor='artifacts/gathering/wall-v14.png', target='artifacts/gathering/wall-v15.png';
const before=fs.readFileSync(ancestor), donor=fs.readFileSync(target), a=decode(before), d=decode(donor);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
if(hash(before)!=='262b4871ab617a9df293f0cd40973748743bd08e8b411f608816c73ffa6461d6')throw Error('Ancestor mismatch');
if(hash(donor)!=='e7b7ff436273065dcba38fd3f735c114154840b2112648c421ec38fe71d64fa1')throw Error('Requires original generated pigment donor; refusing to repaint completed wall');
const box=[360,1000,495,1080], crop=[795,495,1080,750];
let changed=0;
const original=Buffer.from(a.pixels);
function pigment(x,y,color,alpha){const k=(y*a.width+x)*3;for(let c=0;c<3;c++)a.pixels[k+c]=Math.round(a.pixels[k+c]*(1-alpha)+color[c]*alpha);}
for(let n=0;n<2;n++)for(let yy=0;yy<34;yy++)for(let xx=0;xx<34;xx++){
 const sx=Math.floor(crop[0]+xx*(crop[2]-crop[0])/34),sy=Math.floor(crop[1]+yy*(crop[3]-crop[1])/34),j=(sy*d.width+sx)*3;
 const r=d.pixels[j],g=d.pixels[j+1],b=d.pixels[j+2];
 if(r<70||r<g*1.3||r<b*1.5)continue;
 const color=n?[r*.78,g*.82,b*.8]:[Math.min(205,r*.96),Math.min(160,r*.67),Math.min(65,r*.25)];
 pigment(369+n*81+xx,1017+n*16+yy,color,.82);
}
for(let x=407;x<448;x++)for(let dy=-1;dy<=1;dy++){
 const y=1035+Math.round((x-407)*.3)+dy;
 const grain=((x*1237+y*733)%31)/31;
 if((x%13)>8||grain<.18)continue;
 pigment(x,y,[207,182,143],.45+grain*.28);
}
for(let k=0;k<a.pixels.length;k+=3)if(original[k]!==a.pixels[k]||original[k+1]!==a.pixels[k+1]||original[k+2]!==a.pixels[k+2])changed++;
if(changed<100)throw Error('Missing new mark');
fs.writeFileSync(target,encode(a));
fs.writeFileSync('gathering/mark-process15.json',JSON.stringify({method:'Built-in image generation supplied an isolated worn pigment daub. Its pigment was sampled twice, tinted yellow/red ochre and joined by a hand-finished broken chalk thread on bare rock. Black donor background was excluded. All ancestor pixels outside the addition remain exact.',image_tool:'image_gen.imagegen',ancestor,ancestor_sha256:hash(before),generated_donor_sha256:hash(donor),donor_dimensions:[d.width,d.height],donor_crop:crop,destination_box:box,changed_pixels:changed,preservation:'Every decoded pixel outside the addition box is identical to Gathering 14.'},null,2)+'\n');
console.log({width:a.width,height:a.height,changed});
