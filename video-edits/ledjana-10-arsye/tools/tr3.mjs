import { pipeline, env } from '@huggingface/transformers';
import fs from 'fs'; import wf from 'wavefile';
env.allowRemoteModels=false; env.localModelPath='./package/models/';
const p = await pipeline('automatic-speech-recognition','Xenova/whisper-small',{dtype:'q8', device:'cpu'});
const wins = JSON.parse(fs.readFileSync('raw.wins.json')); const out=[];
for (let i=0;i<wins.length;i++){
  const w = new wf.WaveFile(fs.readFileSync(`w/w${i}.wav`)); w.toBitDepth('32f');
  let a = w.getSamples(); if (Array.isArray(a)) a=a[0];
  const off = Math.max(0,wins[i][0]-0.2);
  const r = await p(new Float32Array(a), {language:'albanian', task:'transcribe', return_timestamps:true, no_repeat_ngram_size:3});
  for (const c of r.chunks){ const s=c.timestamp[0]+off, e=(c.timestamp[1]??(wins[i][1]-off))+off; out.push({s,e,text:c.text.trim()}); console.log(s.toFixed(2),e.toFixed(2),'|',c.text.trim()); }
}
fs.writeFileSync('raw.final.json', JSON.stringify(out,null,1));
