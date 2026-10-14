import bpy, math, json
rig=bpy.data.objects['GPT_Girl_Rig']; mesh=bpy.data.objects['GPT_Girl_Desktop_V2']
for p in rig.pose.bones: p.matrix_basis.identity()
bpy.context.view_layer.objects.active=rig; bpy.ops.object.mode_set(mode='EDIT')
eb=rig.data.edit_bones
for side,s in [('L',1),('R',-1)]:
    eb['Clavicle.'+side].tail=(s*.20,-.06,1.53)
    eb['UpperArm.'+side].head=(s*.20,-.06,1.53); eb['UpperArm.'+side].tail=(s*.33,-.15,1.30)
    eb['Forearm.'+side].head=(s*.33,-.15,1.30); eb['Forearm.'+side].tail=(s*.45,-.20,1.10)
    eb['Hand.'+side].head=(s*.45,-.20,1.10); eb['Hand.'+side].tail=(s*.51,-.23,.99)
    eb['Sleeve.'+side].head=(s*.33,-.15,1.30); eb['Sleeve.'+side].tail=(s*.34,-.16,1.05)
bpy.ops.object.mode_set(mode='OBJECT')
names={g.index:g.name for g in mesh.vertex_groups}; count=0
for v in mesh.data.vertices:
    x,y,z=v.co; ax=abs(x); side='L' if x>=0 else 'R'
    if ax>.33 and y<-.075 and .93<z<1.29:
        w={names[g.group]:g.weight for g in v.groups if names[g.group] in ['UpperArm.'+side,'Forearm.'+side,'Hand.'+side,'Sleeve.'+side]}
        total=sum(w.values())
        if total>.15:
            if ax>.425 and z<1.10: w={'Hand.'+side:1}; total=1
            for g in list(v.groups): mesh.vertex_groups[g.group].remove([v.index])
            for n,q in w.items(): mesh.vertex_groups[n].add([v.index],q/total,'REPLACE')
            count+=1
rig.pose.bones['UpperArm.R'].rotation_euler.z=math.radians(38)
rig.pose.bones['Forearm.R'].rotation_euler.z=math.radians(55)
rig.pose.bones['Forearm.R'].rotation_euler.x=math.radians(-12)
rig.pose.bones['Head'].rotation_euler.y=math.radians(-8)
print('Corrected hand and sleeve weights',count)
