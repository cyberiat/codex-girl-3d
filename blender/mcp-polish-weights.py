import bpy, bmesh
rig=bpy.data.objects['GPT_Girl_Rig']; mesh=bpy.data.objects['GPT_Girl_Desktop_V2']
names={g.index:g.name for g in mesh.vertex_groups}; count=0
for v in mesh.data.vertices:
    x,y,z=v.co; side='L' if x>=0 else 'R'
    if abs(x)>.29 and y<.08 and .93<z<1.30:
        w={names[g.group]:g.weight for g in v.groups if names[g.group] in ['UpperArm.'+side,'Forearm.'+side,'Hand.'+side,'Sleeve.'+side]}
        total=sum(w.values())
        if total>.30:
            for g in list(v.groups): mesh.vertex_groups[g.group].remove([v.index])
            for n,q in w.items(): mesh.vertex_groups[n].add([v.index],q/total,'REPLACE')
            count+=1
bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); bpy.context.view_layer.objects.active=mesh
bm=bmesh.new(); bm.from_mesh(mesh.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000008)
bm.to_mesh(mesh.data); bm.free(); mesh.data.update()
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_smooth(group_select_mode='ALL',factor=.45,repeat=3)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL',limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL',lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
print('Polished',count,'sleeve vertices; welded render mesh vertices',len(mesh.data.vertices))
