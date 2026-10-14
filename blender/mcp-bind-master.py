import bpy, json
rig=bpy.data.objects['GPT_Girl_Rig']; mesh=bpy.data.objects['GPT_Girl_Desktop_V2']; high=bpy.data.objects['GPT_Girl_HighRes_Master']
rig.data.pose_position='REST'
high.hide_viewport=False
high.modifiers.clear()
high.hide_set(False)
bpy.ops.object.select_all(action='DESELECT'); high.select_set(True); bpy.context.view_layer.objects.active=high
for g in mesh.vertex_groups:
    if g.name not in high.vertex_groups: high.vertex_groups.new(name=g.name)
transfer=high.modifiers.new('Final animation weights from desktop surface','DATA_TRANSFER'); transfer.object=mesh
transfer.use_vert_data=True; transfer.data_types_verts={'VGROUP_WEIGHTS'}; transfer.vert_mapping='POLYINTERP_NEAREST'
transfer.layers_vgroup_select_src='ALL'; transfer.layers_vgroup_select_dst='NAME'
bpy.ops.object.modifier_apply(modifier=transfer.name)
high.parent=rig
arm=high.modifiers.new('High resolution character deformation','ARMATURE'); arm.object=rig; arm.use_deform_preserve_volume=False
for m in mesh.modifiers:
    if m.type=='ARMATURE': m.use_deform_preserve_volume=False
high.hide_set(True); high.hide_render=True
high.hide_viewport=True
rig.data.pose_position='POSE'
bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active=rig
rig.animation_data.action=bpy.data.actions['Wave']; bpy.context.scene.frame_end=144; bpy.context.scene.frame_set(42)
bpy.ops.wm.save_as_mainfile(filepath='D:/farm/gpt-dragon/blender/GPT-Girl-Desktop-Pet-V2.blend')
print(json.dumps({'master_vertices':len(high.data.vertices),'master_faces':len(high.data.polygons),'master_groups':len(high.vertex_groups),'bound_to':rig.name}))
