import bpy, numpy as np, math, json
from mathutils.kdtree import KDTree
m=bpy.data.objects['GPT_Girl_Desktop_V2']; n=len(m.data.vertices)
co=np.empty(n*3,dtype=np.float64); m.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)
ed=np.empty(len(m.data.edges)*2,dtype=np.int32); m.data.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
names={g.index:g.name for g in m.vertex_groups}; u=np.zeros(n)
for v in m.data.vertices: u[v.index]=sum(g.weight for g in v.groups if names[g.group].startswith(('Hand.','Forearm.','UpperArm.','Sleeve.')))
x=np.abs(co[:,0]); y=co[:,1]; z=co[:,2]
kd=KDTree(n)
for i,p in enumerate(co): kd.insert(p,i)
kd.balance(); extra=[]
for i in np.where((x>.18)&(y<.13)&(z>.88)&(z<1.62))[0]:
    for _,j,d in kd.find_n(co[i],10):
        if j>i and d<.012: extra.append((int(i),j))
if extra: ed=np.concatenate((ed,np.array(extra,dtype=np.int32)))
zero=(x<.18)|(z<.89)|(z>1.61)|(y>.10)
hand=(x>.44)&(y<-.10)&(z>.94)&(z<1.15)
armx=.20+(1.53-z)*.565; army=-.06-(1.53-z)*.39
tube=((x-armx)**2+(y-army)**2<.055**2)&(z>1.27)&(z<1.47)&(x>.235)
one=(hand|tube)&~zero
a,b=ed[:,0],ed[:,1]
length=np.linalg.norm(co[a]-co[b],axis=1)
weight=1/np.maximum(length,.003)
degree=np.bincount(a,weights=weight,minlength=n)+np.bincount(b,weights=weight,minlength=n)
u[zero]=0; u[one]=1
for iteration in range(650):
    s=np.bincount(a,weights=weight*u[b],minlength=n)+np.bincount(b,weights=weight*u[a],minlength=n)
    avg=s/np.maximum(degree,1e-8)
    u=.15*u+.85*avg; u[zero]=0; u[one]=1
def sm(a,b,x):
    t=max(0,min(1,(x-a)/(b-a))); return t*t*(3-2*t)
changed=0
for v in m.data.vertices:
    xx,yy,zz=v.co; ax=abs(xx); side='L' if xx>=0 else 'R'; amount=float(u[v.index])
    original={names[g.group]:g.weight for g in v.groups}
    old=sum(q for k,q in original.items() if k.startswith(('Hand.','Forearm.','UpperArm.','Sleeve.')))
    if amount<.0001 and old<.0001 and not(ax>.22 and yy>.015 and 1.12<zz<1.68): continue
    body={k:q for k,q in original.items() if not k.startswith(('Hand.','Forearm.','UpperArm.','Sleeve.'))}
    if sum(body.values())<.025:
        skirt=1-sm(.98,1.15,zz); spine=sm(1.05,1.28,zz)*(1-skirt); chest=sm(1.30,1.50,zz)
        lr=sm(-.16,.16,xx); back=sm(-.09,.12,yy)
        body={'Hips':max(0,1-skirt-spine-chest),'Spine':spine,'Chest':chest,'Skirt.FrontL':skirt*lr*(1-back),'Skirt.FrontR':skirt*(1-lr)*(1-back),'Skirt.BackL':skirt*lr*back,'Skirt.BackR':skirt*(1-lr)*back}
    # Keep the torso contribution coherent before the four-influence export limit.
    # Otherwise dropping a small sleeve group can abruptly change total arm weight.
    core='Hips' if zz<1.17 else ('Spine' if zz<1.40 else 'Chest')
    hair=sm(-.015,.08,yy)*sm(1.10,1.22,zz)*sm(.19,.27,ax)*(1-sm(1.65,1.78,zz))
    tip=1-sm(1.30,1.51,zz)
    body={core:1-hair,'Hair.'+side:hair*(1-tip*.85),'HairTip.'+side:hair*tip*.85}
    body=sorted(((k,q) for k,q in body.items() if q>.001),key=lambda a:a[1],reverse=True)[:2]
    total=sum(q for k,q in body); w={k:q/total*(1-amount) for k,q in body}
    hw=sm(.40,.46,ax)*(1-sm(1.08,1.17,zz))*(1-sm(-.12,-.06,yy))
    upper=sm(1.26,1.43,zz)*(1-hw)
    fore=max(0,1-hw-upper)
    cloth=(1-sm(.405,.45,ax))*(1-sm(1.18,1.28,zz))*.35*sm(.90,.99,amount)
    for k,q in [('Hand.'+side,hw),('UpperArm.'+side,upper),('Forearm.'+side,fore*(1-cloth)),('Sleeve.'+side,fore*cloth)]:
        w[k]=amount*q
    w=sorted(((k,q) for k,q in w.items() if q>.0001),key=lambda a:a[1],reverse=True)[:4]
    total=sum(q for k,q in w)
    for g in list(v.groups): m.vertex_groups[g.group].remove([v.index])
    for k,q in w: m.vertex_groups[k].add([v.index],q/total,'REPLACE')
    changed+=1
bpy.context.view_layer.update()
print(json.dumps({'harmonic_weight_vertices':changed,'pinned_hand_and_arm':int(one.sum()),'pinned_body':int(zero.sum()),'iterations':650}))
