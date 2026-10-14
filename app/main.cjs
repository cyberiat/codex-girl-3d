const { app, BrowserWindow, ipcMain, Menu, Tray, nativeImage, screen, globalShortcut } = require('electron');
const path = require('node:path');
const fs = require('node:fs');
let win, tray, dragging, ignore = false;
const root = path.join(__dirname, '..');
const verifying=process.argv.includes('--verify');
const verification=[];
const actions = [['Idle','待机'],['Wave','挥手'],['Nod','点头'],['Bow','鞠躬'],['Happy','开心'],['Walk','原地踏步'],['LookAround','看看四周'],['Sleep','打瞌睡']];
function send(action) { win?.webContents.send('pet-action', action); }
function menu() { return Menu.buildFromTemplate([
  {label:'GPT 娘 · 3D 桌宠', enabled:false},
  ...actions.map(([key,label])=>({label,click:()=>send(key)})),
  {type:'separator'},
  {label:'转向左侧', click:()=>send('turn-left')}, {label:'转向右侧',click:()=>send('turn-right')},
  {label:'恢复正面',click:()=>send('front')},
  {label:'放大',click:()=>send('larger')},{label:'缩小',click:()=>send('smaller')},
  {label:'随机小动作',type:'checkbox',checked:!win?.randomOff,click:i=>{win.randomOff=!i.checked;send(i.checked?'random-on':'random-off');}},
  {label:'鼠标穿透（Ctrl+Alt+G 恢复）',type:'checkbox',checked:ignore,click:()=>setIgnore(!ignore)},
  {label:'显示／隐藏',click:()=>win.isVisible()?win.hide():win.showInactive()},
  {type:'separator'},{label:'退出桌宠',click:()=>app.quit()}
]); }
function setIgnore(value) { ignore=value;win.setIgnoreMouseEvents(value,{forward:true});tray?.setContextMenu(menu()); }
if (!app.requestSingleInstanceLock()) app.quit();
else {
 app.on('second-instance',async(_event,argv)=>{
  win?.show();
  if(argv.includes('--diagnose')&&win){
   const state=await win.webContents.executeJavaScript('({ready:document.body.dataset.ready,action:document.body.dataset.action,hidden:document.hidden,error:document.querySelector("#error").textContent})');
   fs.mkdirSync(path.join(root,'verification'),{recursive:true});
   fs.writeFileSync(path.join(root,'verification','live-state.json'),JSON.stringify({state,bounds:win.getBounds(),visible:win.isVisible(),alwaysOnTop:win.isAlwaysOnTop()},null,2));
   fs.writeFileSync(path.join(root,'verification','live-window.png'),(await win.webContents.capturePage()).toPNG());
  }
 });
 app.whenReady().then(()=>{
  const area=screen.getPrimaryDisplay().workArea;
  win=new BrowserWindow({title:'GPT 娘 · 3D 桌宠',width:420,height:600,x:area.x+area.width-440,y:area.y+area.height-600,transparent:true,frame:false,hasShadow:false,alwaysOnTop:true,resizable:false,skipTaskbar:false,backgroundColor:'#00000000',show:false,webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true,backgroundThrottling:false,additionalArguments:verifying?['--verify-pet']:[]}});
  win.setMenu(null);
  win.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  win.webContents.on('will-navigate',e=>e.preventDefault());
  win.webContents.on('console-message',(_event,details,message)=>{fs.appendFileSync(path.join(root,'runtime.log'),(typeof details==='object'?JSON.stringify(details):message)+'\n');});
  win.loadFile(path.join(__dirname,'index.html'));
  win.once('ready-to-show',()=>{win.show();win.setAlwaysOnTop(true,'screen-saver');});
  win.on('show',()=>win.setAlwaysOnTop(true,'screen-saver'));
  tray=new Tray(nativeImage.createFromPath(path.join(root,'assets','gpt-girl-a-pose.png')).resize({width:22,height:32}));
  tray.setToolTip('GPT 娘 · 3D 桌宠');tray.setContextMenu(menu());tray.on('double-click',()=>{setIgnore(false);win.show();});
  globalShortcut.register('Control+Alt+G',()=>{setIgnore(false);win.show();});
  ipcMain.on('menu',()=>menu().popup({window:win}));
  ipcMain.on('drag-start',()=>{dragging={cursor:screen.getCursorScreenPoint(),bounds:win.getBounds()};});
  ipcMain.on('drag-move',()=>{if(!dragging)return;const p=screen.getCursorScreenPoint();win.setPosition(dragging.bounds.x+p.x-dragging.cursor.x,dragging.bounds.y+p.y-dragging.cursor.y);});
  ipcMain.on('drag-end',()=>{dragging=null;});
  ipcMain.handle('model',()=>{
    const p=path.join(root,'assets','gpt-girl-animated-v2.glb');
    if(!fs.existsSync(p)) throw new Error('动画模型尚未生成：assets/gpt-girl-animated-v2.glb');
    return fs.readFileSync(p);
  });
  if(verifying){
    fs.mkdirSync(path.join(root,'verification'),{recursive:true});
    ipcMain.handle('verify-frame',async(_e,data)=>{
      if(!actions.some(([key])=>key===data.name))throw Error('Unknown test clip');
      await new Promise(resolve=>setTimeout(resolve,150));
      const picture=await win.webContents.capturePage();
      fs.writeFileSync(path.join(root,'verification',data.name+'.png'),picture.toPNG());
      verification.push(data);return true;
    });
    ipcMain.handle('verify-done',(_e,data)=>{
      fs.writeFileSync(path.join(root,'verification','report.json'),JSON.stringify({frames:verification,...data},null,2));
      setTimeout(()=>app.quit(),200);return true;
    });
    setTimeout(()=>{fs.appendFileSync(path.join(root,'runtime.log'),'Verification timeout\n');app.exit(2);},90000).unref();
  }
 });
 app.on('will-quit',()=>globalShortcut.unregisterAll());
 app.on('window-all-closed',()=>app.quit());
}
