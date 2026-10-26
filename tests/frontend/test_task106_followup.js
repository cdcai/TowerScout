const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.join(__dirname, '../../webapp/js/src');
const source = file => fs.readFileSync(path.join(root, file), 'utf8');
const logger = {debug(){}, info(){}, warn(){}, error(){}};

function providerChecks() {
  const detections = [], notices = [], visibility = [];
  const c = {console, TowerScoutLogger:logger,
    PlaceRect:class {update(){}}, reviewCheckBox:{checked:false}, Detection_minConfidence:.5,
    Tile:{getTileIds:()=>[0]}, Tile_tiles:[{}],
    providerManager:{getTilesArrayDirect:()=>[{id:0,x1:10,x2:20,y1:50,y2:40}]},
    TowerScoutErrorHandler:{showUserNotification:(...a)=>notices.push(a)}};
  c.window=c; vm.createContext(c);
  for(const f of ['utils/polygonValidation.js','providers/TSMap_base.js','providers/GoogleMap.js','providers/AzureMap.js','detection/Detection.js']) vm.runInContext(source(f),c);
  const update=c.Detection.prototype.update;
  c.Detection=class {constructor(...args){this.inside=args[8];this.args=args;detections.push(this);} static generateList(){}};
  const A=[[[10,40],[15,40],[15,45],[10,45]]];
  const B=[{points:[[16,46],[20,46],[20,50],[16,50]]}];
  for(const provider of ['GoogleMap','AzureMap']) for(const current of [B,[]]) for(const unknown of [false,true]) for(const outside of [false,true]) {
    c.TSMap.setDetectionBoundaries(unknown ? null : JSON.stringify(A));
    const obj=Object.create(c[provider].prototype);
    const x=outside ? 17 : 11, y=outside ? 47 : 41;
    const shape={bounds:{getSouthWest:()=>({lng:()=>x,lat:()=>y}),getNorthEast:()=>({lng:()=>x+1,lat:()=>y+1})},setMap(){}};
    Object.assign(obj,{boundaries:current,newShapes:[shape],isDrawing:false,geocodeDetection(){},getPendingBoundaryShapes(){return this.newShapes},validateDrawnShapes(){return {valid:true}},extractBoundaryPointsFromShape(){return [[x,y],[x+1,y],[x+1,y+1],[x,y+1]]}});
    obj.addShapes();
    assert.strictEqual(detections.at(-1).inside, !unknown && !outside, `${provider}: stored run membership`);
    const det={...detections.at(-1), idInTile:-1, selected:true, conf:1, id:0,map:{updateMapRect:(_,show)=>visibility.push(show)}};
    update.call(det);
    assert.strictEqual(visibility.at(-1),true,'selected manual remains visible without falsifying membership');
    det.selected=false; update.call(det);
    assert.strictEqual(visibility.at(-1),false,'unchecked manual remains hidden');
  }
  c.TSMap.setDetectionBoundaries(JSON.stringify(A));
  A[0][0][0]=99;
  assert.strictEqual(c.TSMap.detectionBoundaries[0].points[0][0],10,'snapshot owns its coordinates');
  assert(notices.some(n=>n[0].includes('unconfirmed')));
  c.providerManager.getTiles=()=>[];
  c.providerManager.clearTiles=()=>{};
  vm.runInContext(source('detection/Tile.js'),c);
  c.Tile.resetAll();
  assert.strictEqual(c.TSMap.detectionBoundaries,null,'actual restore/new-run tile reset discards old membership context');
}

async function uploadChecks() {
  const errors=[], changes=[], input={files:[{name:'synthetic.png'}],value:'selected'}, canvas={src:'previous'};
  const c={console,FormData:class{append(){}},document:{getElementById:id=>id==='canvas'?canvas:input},
    $:()=>({val:()=>0}),Detection:{resetAll:()=>changes.push('reset')},TowerScoutLogger:logger,
    TowerScoutErrorHandler:{showUserNotification:m=>errors.push(m)}};
  c.window=c; vm.createContext(c);
  const text=source('towerscout.js');
  vm.runInContext(text.slice(text.indexOf('async function uploadImage()'),text.indexOf('async function uploadDataset()')),c);
  for(const header of [null,'https://example.invalid/image.png','/uploads/other.png','//example.invalid/x', '/uploads/'+'a'.repeat(32)+'.png?key=synthetic']) {
    c.fetch=async()=>({ok:true,json:async()=>[[]],headers:{get:()=>header}});
    await c.uploadImage();
    assert.strictEqual(canvas.src,'previous'); assert.strictEqual(changes.length,0);
    assert.strictEqual(input.value,'');
  }
  c.fetch=async()=>({ok:false,status:429,json:async()=>({error:true,message:'Detection already running'})});
  await c.uploadImage(); assert(errors.at(-1).includes('Detection already running'));
  const url='/uploads/'+'b'.repeat(32)+'.webp';
  c.fetch=async()=>({ok:true,json:async()=>[[]],headers:{get:()=>url}});
  await c.uploadImage(); assert.strictEqual(canvas.src,url); assert.strictEqual(changes.length,1);
}

function listAndEscapingChecks() {
  const visibility=[], addresses=[];
  const manual={id:0,idInTile:-1,inside:false,conf:1,selected:true,
    show:v=>visibility.push(v),update(){},showAddr:v=>addresses.push(v)};
  manual.firstDet=manual;
  const c={console,PlaceRect:class{},confSlider:{value:50},reviewCheckBox:{checked:false},
    Detection_minConfidence:.5,TowerScoutLogger:logger,
    document:{getElementById:()=>null},
    providerManager:{setMinConfidence(){},getDetections:()=>[manual]}};
  c.window=c;vm.createContext(c);
  vm.runInContext(source('detection/DetectionList.js'),c);
  vm.runInContext(source('detection/Detection.js'),c);
  c.adjustConfidence();
  assert.deepStrictEqual(visibility,[true],'outside manual stays in the detection list');
  assert.deepStrictEqual(addresses,[true],'outside manual keeps its address row');
  assert.strictEqual(c.Detection.escapeHtml(`"quoted" 'single' <tag> &`),
    '&quot;quoted&quot; &#39;single&#39; &lt;tag&gt; &amp;');
}

function finalWarningChecks() {
  for(const provider of ['GoogleMap','AzureMap']) for(const unknown of [false,true]) {
    const nodes={},notices=[],timers=[],detections=[];
    const c={console,PlaceRect:class{update(){}},reviewCheckBox:{checked:false},Detection_minConfidence:.5,
      Tile:{getTileIds:()=>[0]},Tile_tiles:[{}],
      providerManager:{getTilesArrayDirect:()=>[{id:0,x1:10,x2:20,y1:50,y2:40}]},
      document:{getElementById:id=>nodes[id],createElement:()=>({style:{}}),
        body:{appendChild:n=>{nodes[n.id]=n;}}},
      timerManager:{clearTimeout(){},setTimeout:(_,ms)=>{timers.push(ms);return timers.length;}},
      TowerScoutLogger:{...logger,info:m=>notices.push(m)}};
    c.window=c;vm.createContext(c);
    for(const file of ['managers/ErrorHandler.js','utils/polygonValidation.js',
      'providers/TSMap_base.js','providers/GoogleMap.js','providers/AzureMap.js']) vm.runInContext(source(file),c);
    c.Detection=class{constructor(...args){detections.push({inside:args[8]});}static generateList(){}};
    c.TSMap.setDetectionBoundaries(unknown ? null : JSON.stringify([[[10,40],[15,40],[15,45],[10,45]]]));
    const obj=Object.create(c[provider].prototype),x=11,y=41;
    const shape={bounds:{getSouthWest:()=>({lng:()=>x,lat:()=>y}),getNorthEast:()=>({lng:()=>x+1,lat:()=>y+1})},setMap(){}};
    Object.assign(obj,{boundaries:[],newShapes:[shape],isDrawing:false,geocodeDetection(){},
      getPendingBoundaryShapes(){return this.newShapes},validateDrawnShapes(){return {valid:true}},
      extractBoundaryPointsFromShape(){return [[x,y],[x+1,y],[x+1,y+1],[x,y+1]]}});
    obj.addShapes();
    assert.strictEqual(detections[0].inside,!unknown);
    const final=nodes['error-notification'];
    if(unknown) {
      assert(final.textContent.includes('unconfirmed'),`${provider}: final visible warning`);
      assert.strictEqual(final.style.backgroundColor,'#f39c12');
      assert.strictEqual(timers.at(-1),8000);
    } else if(provider==='AzureMap') {
      assert(final.textContent.includes('Successfully added 1 manual tower'));
      assert.strictEqual(final.style.backgroundColor,'#27ae60');
    }
  }
}

async function main(){providerChecks();listAndEscapingChecks();finalWarningChecks();await uploadChecks();console.log('Both providers: boundary, final warning, list visibility, escaping and upload contracts pass');}
main().catch(e=>{console.error(e);process.exitCode=1;});
