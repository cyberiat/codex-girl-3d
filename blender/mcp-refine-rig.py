import bpy, math, json
scene=bpy.context.scene; rig=bpy.data.objects['GPT_Girl_Rig']; mesh=bpy.data.objects['GPT_Girl_Desktop_V2']
rig.animation_data.action=None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position='REST'
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT'); eb=rig.data.edit_bones
def bone(name,head,tail,parent):
    b=eb.new(name); b.head=head; b.tail=tail; b.parent=eb[parent]; return b
bone('Neck',(0,0,1.58),(0,0,1.67),'Chest'); eb['Head'].parent=eb['Neck']
for side,s in [('L',1),('R',-1)]:
    bone('Clavicle.'+side,(s*.035,0,1.52),(s*.19,-.025,1.54),'Chest')
    eb['UpperArm.'+side].parent=eb['Clavicle.'+side]
    eb['Hair.'+side].tail=(s*.255,.16,1.42)
    bone('HairTip.'+side,(s*.255,.16,1.42),(s*.31,.20,1.10),'Hair.'+side)
    bone('Sleeve.'+side,(s*.32,-.04,1.30),(s*.30,-.05,1.02),'Forearm.'+side)
for name,x,y in [('FrontL',.19,-.18),('FrontR',-.19,-.18),('BackL',.19,.20),('BackR',-.19,.20)]:
    bone('Skirt.'+name,(x*.7,y*.7,.95),(x,y,.53),'Skirt')
    bone('Hem.'+name,(x,y,.53),(x*1.5,y*1.5,.27),'Skirt.'+name)
bpy.ops.object.mode_set(mode='OBJECT')
groups={g.name:g for g in mesh.vertex_groups}
for b in rig.data.bones:
    if b.name not in groups: groups[b.name]=mesh.vertex_groups.new(name=b.name)
names={g.index:g.name for g in mesh.vertex_groups}
def smooth(a,b,v):
    t=max(0,min(1,(v-a)/(b-a))); return t*t*(3-2*t)
for v in mesh.data.vertices:
    x,y,z=v.co; side='L' if x>=0 else 'R'
    w={names[g.group]:g.weight for g in v.groups}
    # Divide existing Blender-transferred cloth weights into overlapping panels.
    sw=w.pop('Skirt',0)
    if sw:
        lr=smooth(-.16,.16,x); back=smooth(-.09,.12,y); hem=1-smooth(.42,.65,z)
        for tag,q in [('FrontL',lr*(1-back)),('FrontR',(1-lr)*(1-back)),('BackL',lr*back),('BackR',(1-lr)*back)]:
            w['Skirt.'+tag]=sw*q*(1-hem*.78); w['Hem.'+tag]=sw*q*hem*.78
    # Long rear locks follow the head, then bend in a separate tip segment.
    hair=smooth(.09,.22,y)*smooth(1.045,1.22,z)*(1-smooth(1.77,1.88,z))
    if hair>.01:
        w={k:q*(1-hair*.95) for k,q in w.items()}
        w['Hair.'+side]=w.get('Hair.'+side,0)+hair*.95
    for s in ['L','R']:
        hw=w.get('Hair.'+s,0); tip=(1-smooth(1.30,1.51,z))*.85
        w['Hair.'+s]=hw*(1-tip); w['HairTip.'+s]=hw*tip
        fw=w.get('Forearm.'+s,0)
        # Cloth below the arm centerline can trail without pulling the fingers.
        arm_z=1.30-(abs(x)-.32)*1.63
        cloth=(1-smooth(arm_z-.10,arm_z-.02,z))*smooth(.99,1.10,z)*.50
        w['Forearm.'+s]=fw*(1-cloth); w['Sleeve.'+s]=fw*cloth
    if z>1.56 and z<1.72:
        q=w.get('Head',0)*.35*(1-smooth(1.63,1.72,z)); w['Head']=w.get('Head',0)-q; w['Neck']=q
    # Keep at most four meaningful influences for matching Blender/glTF deformation.
    w=sorted(((k,q) for k,q in w.items() if q>.0001),key=lambda a:a[1],reverse=True)[:4]
    total=sum(q for k,q in w)
    for g in list(v.groups): mesh.vertex_groups[g.group].remove([v.index])
    for k,q in w: groups[k].add([v.index],q/total,'REPLACE')
rig.data.pose_position='POSE'
for p in rig.pose.bones: p.rotation_mode='XYZ'
rig.pose.bones['UpperArm.R'].rotation_euler.z=math.radians(38)
rig.pose.bones['Forearm.R'].rotation_euler.z=math.radians(55)
rig.pose.bones['Forearm.R'].rotation_euler.x=math.radians(-12)
rig.pose.bones['Head'].rotation_euler.y=math.radians(-8)
rig.show_in_front=False
bpy.context.view_layer.update()
print(json.dumps({'bones':len(rig.data.bones),'vertices':len(mesh.data.vertices),'unweighted':sum(not v.groups for v in mesh.data.vertices),'max_influences':max(len(v.groups) for v in mesh.data.vertices)}))
