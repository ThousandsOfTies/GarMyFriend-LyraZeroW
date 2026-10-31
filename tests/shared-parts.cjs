'use strict';
// Run the library's own two-instance pages outside this Product adapter.
const {chromium}=require('playwright');
const {spawn}=require('node:child_process');
const path=require('node:path');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const shared=path.resolve(__dirname,'../sources/gar-tools/web-simulator');
const reports=[];
(async()=>{
  const browser=await chromium.launch({channel:process.platform==='win32'?'msedge':undefined,headless:true});
  try{
    for(const fixture of ['display-browser','input-browser']){
      const server=spawn(process.env.PYTHON||'python',[path.join(shared,'serve.py'),'--panel',path.join(shared,'tests',fixture),'--port','0'],{windowsHide:true,stdio:['ignore','pipe','pipe']});
      let output='',errors='';server.stderr.on('data',data=>errors+=data);
      try{
        const url=await new Promise((resolve,reject)=>{
          const timeout=setTimeout(()=>reject(new Error('Shared test server startup timed out: '+errors)),15000);
          server.once('error',error=>{clearTimeout(timeout);reject(error);});
          server.once('exit',code=>{clearTimeout(timeout);reject(new Error('Shared test server exited: '+code+' '+errors));});
          server.stdout.on('data',data=>{output+=data;const match=output.match(/http:\/\/127\.0\.0\.1:\d+/);if(match){clearTimeout(timeout);resolve(match[0]);}});
        });
        const page=await browser.newPage();
        try{
          await page.goto(url);
          await page.waitForFunction(()=>document.documentElement.dataset.testResult,{timeout:15000});
          const result=await page.locator('#results').innerText();
          assert.equal(await page.locator('html').getAttribute('data-test-result'),'pass',result);
          reports.push({fixture,result});console.log('PASS: shared '+fixture+'\n'+result);
        }finally{await page.close();}
      }finally{server.kill();}
    }
    fs.mkdirSync('artifacts',{recursive:true});fs.writeFileSync('artifacts/shared-parts.json',JSON.stringify(reports,null,2)+'\n');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
