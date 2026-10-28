const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:4440,height:1000}});
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(500);
const els=await p.$$('.s');
for(let i=0;i<els.length;i++){await els[i].screenshot({path:`prev/s${i}.png`});}
await b.close();})();
