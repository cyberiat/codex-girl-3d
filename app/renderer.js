import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0x000000,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1;document.body.prepend(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(28,innerWidth/innerHeight,.01,100);
camera.position.set(0,1.05,4.6);camera.lookAt(0,1,0);
scene.add(new THREE.HemisphereLight(0xe5ffff,0x72717e,1.8));
for(const [x,y,z,color,intensity] of [[-3,4,5,0xfff7ec,1.8],[3,2,1,0xd6fff8,1],[1,4,-3,0xffffff,1.4]]){const l=new THREE.DirectionalLight(color,intensity);l.position.set(x,y,z);scene.add(l);}
const pivot=new THREE.Group();scene.add(pivot);
let mixer,current,model,clips={},targetRotation=0,zoom=1,random=true,elapsed=0,returnAt=0,nextRandom=14,paused=false,verifying=window.pet.verifying;
const bubble=document.querySelector('#bubble');let bubbleTimer;
function say(text){bubble.textContent=text;bubble.style.opacity='1';clearTimeout(bubbleTimer);bubbleTimer=setTimeout(()=>bubble.style.opacity='0',3200);}
const messages={Wave:'嗨，我在这里。',Nod:'嗯，明白啦。',Bow:'很高兴陪着你。',Happy:'又完成了一点点！',Walk:'活动一下～',LookAround:'让我看看。',Sleep:'稍微休息一下…'};
function play(name){if(!mixer||!clips[name])return;const action=mixer.clipAction(clips[name]);action.reset().setEffectiveTimeScale(1).setEffectiveWeight(1);action.setLoop(name==='Idle'?THREE.LoopRepeat:THREE.LoopOnce,name==='Idle'?Infinity:1);action.clampWhenFinished=name!=='Idle';action.fadeIn(.3).play();if(current&&current!==action)current.fadeOut(.3);current=action;returnAt=name==='Idle'?0:elapsed+clips[name].duration;document.body.dataset.action=name;if(messages[name])say(messages[name]);}
function command(key){if(key==='turn-left')targetRotation-=Math.PI/4;else if(key==='turn-right')targetRotation+=Math.PI/4;else if(key==='front')targetRotation=pivot.rotation.y+Math.atan2(-Math.sin(pivot.rotation.y),Math.cos(pivot.rotation.y));else if(key==='larger')zoom=Math.min(1.35,zoom+.1);else if(key==='smaller')zoom=Math.max(.65,zoom-.1);else if(key==='random-on')random=true;else if(key==='random-off')random=false;else play(key);}
window.pet.onAction(command);
document.querySelector('#wave').onclick=()=>play('Wave');document.querySelector('#happy').onclick=()=>play('Happy');document.querySelector('#menu').onclick=()=>window.pet.menu();
addEventListener('contextmenu',e=>{e.preventDefault();window.pet.menu();});
let down=false,startX=0,startY=0,moved=false,rotating=false;
renderer.domElement.addEventListener('pointerdown',e=>{if(e.button!==0)return;down=true;moved=false;startX=e.clientX;startY=e.clientY;rotating=e.shiftKey;renderer.domElement.setPointerCapture(e.pointerId);if(!rotating)window.pet.dragStart();});
renderer.domElement.addEventListener('pointermove',e=>{if(!down)return;if(Math.abs(e.clientX-startX)+Math.abs(e.clientY-startY)>4)moved=true;if(rotating){targetRotation+=(e.clientX-startX)*.015;startX=e.clientX;}else window.pet.dragMove();});
function end(){if(!down)return;down=false;window.pet.dragEnd();if(!moved)play('Wave');}
renderer.domElement.addEventListener('pointerup',end);renderer.domElement.addEventListener('lostpointercapture',end);addEventListener('blur',end);
renderer.domElement.title='滚轮旋转 · Ctrl + 滚轮缩放 · Shift + 拖动旋转';
renderer.domElement.addEventListener('wheel',e=>{
 e.preventDefault();
 const unit=e.deltaMode===WheelEvent.DOM_DELTA_LINE?16:e.deltaMode===WheelEvent.DOM_DELTA_PAGE?innerHeight:1;
 const delta=(Math.abs(e.deltaY)>=Math.abs(e.deltaX)?e.deltaY:e.deltaX)*unit;
 if(e.ctrlKey)zoom=THREE.MathUtils.clamp(zoom-delta*.0008,.65,1.35);
 else targetRotation+=delta*.003;
},{passive:false});
document.addEventListener('visibilitychange',()=>paused=document.hidden);
try{const data=await window.pet.model();const buf=data.buffer.slice(data.byteOffset,data.byteOffset+data.byteLength);const gltf=await new GLTFLoader().parseAsync(buf,'');model=gltf.scene;pivot.add(model);const box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const s=1.95/size.y;model.scale.setScalar(s);model.position.set(-center.x*s,-box.min.y*s,-center.z*s);model.traverse(o=>{if(o.isMesh){o.frustumCulled=false;for(const m of (Array.isArray(o.material)?o.material:[o.material])){m.side=THREE.DoubleSide;m.metalness=Math.min(m.metalness??0,.15);m.roughness=Math.max(m.roughness??.6,.55);}}});mixer=new THREE.AnimationMixer(model);for(const c of gltf.animations)clips[c.name]=c;play('Idle');say('你好，我是 GPT 娘。拖动我，右键看更多动作。');console.log('MODEL_READY',JSON.stringify({clips:Object.keys(clips),meshes:scene.children.length}));document.body.dataset.ready='true';}catch(e){document.querySelector('#error').style.display='block';document.querySelector('#error').textContent='模型加载失败\n'+e.message;say('还没有准备好');console.error(e);}
const clock=new THREE.Clock();let frameTime=0;
function tick(){requestAnimationFrame(tick);const dt=Math.min(clock.getDelta(),.1);if(paused||verifying)return;frameTime+=dt;if(frameTime<1/30)return;const delta=frameTime;frameTime=0;elapsed+=delta;mixer?.update(delta);if(returnAt&&elapsed>returnAt)play('Idle');if(random&&elapsed>nextRandom){if(!returnAt)play(['Nod','LookAround','Happy'][Math.floor(Math.random()*3)]);nextRandom=elapsed+20+Math.random()*20;}pivot.rotation.y=THREE.MathUtils.damp(pivot.rotation.y,targetRotation,5,delta);camera.zoom=THREE.MathUtils.damp(camera.zoom,zoom,6,delta);camera.updateProjectionMatrix();renderer.render(scene,camera);}tick();
if(verifying){
 const errors=[];const required=['Idle','Wave','Nod','Bow','Happy','Walk','LookAround','Sleep'];
 let skinned=0,triangles=0;model?.traverse(o=>{if(o.isSkinnedMesh){skinned++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;}});
 if(!skinned)errors.push('No skinned mesh');
 for(const name of required){
  const clip=clips[name];if(!clip){errors.push('Missing '+name);continue;}
  mixer.stopAllAction();const testAction=mixer.clipAction(clip).reset().setLoop(THREE.LoopOnce,1);testAction.clampWhenFinished=true;testAction.play();
  const motionBounds=new THREE.Box3(),point=new THREE.Vector3();let finiteSamples=true;const handPositions=[];
  for(let i=0;i<=12;i++){
   mixer.setTime(clip.duration*i/12);scene.updateMatrixWorld(true);
   model.traverse(o=>{if(o.isSkinnedMesh){o.skeleton.update();const position=o.geometry.attributes.position;const step=Math.max(1,Math.floor(position.count/2500));for(let j=0;j<position.count;j+=step){point.fromBufferAttribute(position,j);o.applyBoneTransform(j,point);point.applyMatrix4(o.matrixWorld);if(!point.toArray().every(Number.isFinite))finiteSamples=false;motionBounds.expandByPoint(point);}}if(o.isBone&&/^Hand[._]?R$/.test(o.name))handPositions.push(o.getWorldPosition(new THREE.Vector3()).toArray());});
  }
  if(!finiteSamples)errors.push('Nonfinite skin deformation in '+name);
  const snapshot={Wave:.32,Happy:.28,Bow:.38,Walk:.2,LookAround:.65,Nod:.28,Sleep:.55,Idle:.42}[name];
  testAction.reset().play();mixer.setTime(clip.duration*snapshot);
  scene.updateMatrixWorld(true);let finite=true,bones=0;
  model.traverse(o=>{if(o.isBone){bones++;if(!o.matrixWorld.elements.every(Number.isFinite))finite=false;}});
  if(!finite)errors.push('Nonfinite bone transform in '+name);
  clearTimeout(bubbleTimer);bubble.style.display='none';renderer.render(scene,camera);
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  await window.pet.verifyFrame({name,duration:clip.duration,tracks:clip.tracks.length,bones,finite,finiteSamples,motionBounds:{min:motionBounds.min.toArray(),max:motionBounds.max.toArray()},rightHandTravel:handPositions.length?Math.max(...handPositions.map(p=>new THREE.Vector3(...p).distanceTo(new THREE.Vector3(...handPositions[0])))):null});
 }
 await window.pet.verifyDone({passed:errors.length===0,errors,skinned,triangles,renderer:renderer.info.render,transparent:renderer.getClearAlpha()===0});
}
