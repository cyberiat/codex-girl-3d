import bpy, json, time
scene=bpy.context.scene
rig=bpy.data.objects['GPT_Girl_Rig']
rig.data.pose_position='REST'
high=bpy.data.objects['Mesh_0']
high.name='GPT_Girl_HighRes_Master'
high.modifiers.clear()
mesh=high.copy(); mesh.data=high.data.copy()
scene.collection.objects.link(mesh); mesh.name='GPT_Girl_Desktop_V2'
high.hide_set(True); high.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); bpy.context.view_layer.objects.active=mesh
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
dec=mesh.modifiers.new('Desktop detail optimization','DECIMATE')
dec.ratio=0.045
dec.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=dec.name)
print('OPTIMIZED',len(mesh.data.vertices),len(mesh.data.polygons))
low=bpy.data.objects['GPT_Girl_Mesh']; low.hide_set(False)
for group in low.vertex_groups:
    mesh.vertex_groups.new(name=group.name)
transfer=mesh.modifiers.new('Blender surface weight transfer','DATA_TRANSFER')
transfer.object=low; transfer.use_vert_data=True
transfer.data_types_verts={'VGROUP_WEIGHTS'}
transfer.vert_mapping='POLYINTERP_NEAREST'
transfer.layers_vgroup_select_src='ALL'; transfer.layers_vgroup_select_dst='NAME'
bpy.ops.object.modifier_apply(modifier=transfer.name)
low.hide_set(True)
mesh.parent=rig
arm=mesh.modifiers.new('Character deformation','ARMATURE'); arm.object=rig
arm.use_deform_preserve_volume=True
for poly in mesh.data.polygons: poly.use_smooth=True
rig.data.pose_position='POSE'
rig.animation_data.action=None
for pb in rig.pose.bones: pb.matrix_basis.identity()
scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath='D:/farm/gpt-dragon/blender/GPT-Girl-V2-MCP-working.blend')
print(json.dumps({'vertices':len(mesh.data.vertices),'faces':len(mesh.data.polygons),'groups':len(mesh.vertex_groups),'unweighted':sum(not v.groups for v in mesh.data.vertices)}))
