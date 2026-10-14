import bpy, math
mesh=bpy.data.objects['GPT_Girl_Desktop_V2']
names={g.index:g.name for g in mesh.vertex_groups}
def sm(a,b,x):
    t=max(0,min(1,(x-a)/(b-a))); return t*t*(3-2*t)
count=0
for v in mesh.data.vertices:
    x,y,z=v.co; ax=abs(x); side='L' if x>=0 else 'R'
    if z>1.27: continue
    w={names[g.group]:g.weight for g in v.groups}
    arm={k:q for k,q in w.items() if k.startswith(('Hand.','Forearm.','UpperArm.','Sleeve.'))}
    aw=sum(arm.values())
    if aw<.0001: continue
    # At waist height the sleeve/hand is well in front of the skirt and farther out.
    # The old z-only hand assignment also captured the side skirt and ribbons.
    edge=.27+max(0,1.17-z)*.65
    gate=sm(edge,edge+.055,ax)*(1-sm(-.15,-.065,y))*sm(.90,.96,z)
    if ax>.425 and y<-.095 and z>.94: gate=1
    gate=gate*(1-sm(1.16,1.27,z))+sm(1.16,1.27,z)
    target=aw*gate
    body={k:q for k,q in w.items() if k not in arm}
    if sum(body.values())<.01:
        skirt=1-sm(1.00,1.17,z)
        lr=sm(-.16,.16,x); back=sm(-.09,.12,y)
        body={'Hips':1-skirt,'Skirt.FrontL':skirt*lr*(1-back),'Skirt.FrontR':skirt*(1-lr)*(1-back),'Skirt.BackL':skirt*lr*back,'Skirt.BackR':skirt*(1-lr)*back}
    total=sum(body.values()); w={k:q/total*(1-target) for k,q in body.items() if q>0}
    w.update({k:q/aw*target for k,q in arm.items()})
    if ax>.44 and y<-.11 and .94<z<1.09: w={'Hand.'+side:1}
    w=sorted(((k,q) for k,q in w.items() if q>.0001),key=lambda x:x[1],reverse=True)[:4]
    total=sum(q for k,q in w)
    for g in list(v.groups): mesh.vertex_groups[g.group].remove([v.index])
    for k,q in w: mesh.vertex_groups[k].add([v.index],q/total,'REPLACE')
    count+=1
bpy.context.view_layer.update()
print('Removed misplaced arm influence from lower garment region:',count)
