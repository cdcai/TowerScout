const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.resolve(__dirname, '../..');
const logger = {debug(){},info(){},warn(){},error(){}};

async function main() {
  const c = {console, PlaceRect:class {}, providerManager:{getTilesArrayDirect:()=>[
    {metadata:'<img src=x onerror="synthetic()">'}]}, TowerScoutLogger:logger};
  c.window=c; vm.createContext(c);
  vm.runInContext(fs.readFileSync(path.join(root,'webapp/js/src/detection/Detection.js'),'utf8'),c);
  const html=c.Detection.prototype.generateCheckBox.call({tile:0,secondary:0,conf:.8,idInTile:0,id:0,selected:true});
  assert(!html.includes('<img'));
  assert(html.includes('&lt;img'));

  const source=fs.readFileSync(path.join(root,'webapp/js/src/towerscout.js'),'utf8');
  const fn=source.slice(source.indexOf('async function uploadDataset()'),source.indexOf('function estimateNumTiles'));
  const changes=[], errors=[];
  const input={files:[{}],value:'selected'};
  const ctx={console,Detection_detections:[{}],confirm:()=>true,performance:{now:()=>0},
    FormData:class{append(){}}, document:{getElementById:()=>input},
    Detection:{resetAll:()=>changes.push('detections')}, Tile:{resetAll:()=>changes.push('tiles')},
    currentMap:{clearShapes:()=>changes.push('shapes'),resetBoundaries:()=>changes.push('boundaries')},
    processObjects:()=>changes.push('process'),TowerScoutLogger:logger,
    TowerScoutErrorHandler:{showUserNotification:m=>errors.push(m)},disableProgress(){}};
  ctx.window=ctx;vm.createContext(ctx);vm.runInContext(fn,ctx);
  ctx.fetch=async()=>({ok:false,status:400,json:async()=>({error:'Invalid dataset metadata'})});
  await ctx.uploadDataset();
  assert.deepStrictEqual(changes,[],'failure must preserve visible review/export state');
  assert(errors[0].includes('Invalid dataset metadata'),'preserve actionable server error');
  assert.strictEqual(input.value,'','allow retry with the same filename');
  ctx.fetch=async()=>({ok:false,status:429,json:async()=>({error:true,message:'Wait for current upload'})});
  await ctx.uploadDataset();
  assert(errors.at(-1).includes('Wait for current upload'));
  assert.deepStrictEqual(changes,[]);
  ctx.fetch=async()=>({ok:true,json:async()=>[]});
  await ctx.uploadDataset();
  assert.deepStrictEqual(changes,['detections','tiles','shapes','boundaries','process']);

  vm.runInContext(fs.readFileSync(path.join(root,'webapp/js/src/managers/ErrorHandler.js'),'utf8'),c);
  let notifications=0;c.TowerScoutErrorHandler.handleNetworkError=()=>notifications++;
  for(const name of ['AbortError','TypeError']) {
    await assert.rejects(c.TowerScoutErrorHandler.wrapNetworkCall(async()=>{throw Object.assign(new Error('synthetic'),{name});})());
  }
  assert.strictEqual(notifications,1,'only genuine network failures notify');
  vm.runInContext(fs.readFileSync(path.join(root,'webapp/js/src/utils/polygonValidation.js'),'utf8'),c);
  const intersects=c.PolygonValidation.rectangleIntersectsBoundaries;
  const bounds=[{points:[[0,0],[2,0],[2,2],[0,2]]}];
  assert(intersects(1,3,3,1,bounds),'straddling rectangle intersects');
  assert(!intersects(3,4,4,3,bounds),'manual selection does not imply boundary membership');
  assert(intersects(.5,1.5,1.5,.5,bounds));
  assert(intersects(-1,3,3,-1,bounds));
  console.log('Restore state, metadata escaping and real cancellation wrapper: pass');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
