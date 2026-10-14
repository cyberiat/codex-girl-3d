const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('pet',{
 model:()=>ipcRenderer.invoke('model'),menu:()=>ipcRenderer.send('menu'),
 dragStart:()=>ipcRenderer.send('drag-start'),dragMove:()=>ipcRenderer.send('drag-move'),dragEnd:()=>ipcRenderer.send('drag-end'),
 onAction:fn=>ipcRenderer.on('pet-action',(_e,key)=>fn(key))
 ,verifying:process.argv.includes('--verify-pet')
 ,verifyFrame:data=>ipcRenderer.invoke('verify-frame',data)
 ,verifyDone:data=>ipcRenderer.invoke('verify-done',data)
});
