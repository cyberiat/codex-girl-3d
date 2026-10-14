import bpy, json, math
from mathutils import Vector
scene=bpy.context.scene; rig=bpy.data.objects['GPT_Girl_Rig']; mesh=bpy.data.objects['GPT_Girl_Desktop_V2']
bpy.data.objects['GPT_Girl_HighRes_Master'].hide_viewport=True
report={'blender':bpy.app.version_string,'workflow':'MCP for Blender 2.1.9; live Blender scene editing and Blender glTF exporter','source':'Meshy_AI_Aqua_Seraphina_1014082804_texture.glb','vertices':len(mesh.data.vertices),'triangles':len(mesh.data.polygons),'bones':len(rig.data.bones),'unweighted':sum(not v.groups for v in mesh.data.vertices),'actions':{}}
for a in bpy.data.actions:
    rig.animation_data.action=a
    lo,hi=map(int,a.frame_range); valid=True; maximum=0
    for f in range(lo,hi+1,3):
        scene.frame_set(f)
        for p in rig.pose.bones:
            valid &= all(math.isfinite(v) for row in p.matrix for v in row)
    scene.frame_set(lo); start={p.name:p.matrix.copy() for p in rig.pose.bones}
    scene.frame_set(hi)
    seam=max(abs(p.matrix[i][j]-start[p.name][i][j]) for p in rig.pose.bones for i in range(4) for j in range(4))
    report['actions'][a.name]={'frames':hi-lo,'seconds':(hi-lo)/30,'finite':valid,'loop_pose_error':seam}
rig.animation_data.action=bpy.data.actions['Idle']; scene.frame_start=0; scene.frame_end=180; scene.frame_set(0)
rig.data.pose_position='POSE'
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active=rig
scene.render.engine='CYCLES'; scene.render.resolution_x=640; scene.render.resolution_y=800
for workspace in bpy.data.workspaces:
    for screen in workspace.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=3.7
                area.spaces.active.region_3d.view_location=(0,0,1)
                area.spaces.active.shading.type='MATERIAL'
                area.spaces.active.overlay.show_overlays=False
rig['animation_notes']='V2: 35 bones, 8 actions, original high resolution master retained hidden. Large gestures with corrected hand weights and delayed secondary motion.'
bpy.ops.wm.save_as_mainfile(filepath='D:/farm/gpt-dragon/blender/GPT-Girl-Desktop-Pet-V2.blend')
bpy.ops.export_scene.gltf(filepath='D:/farm/gpt-dragon/assets/gpt-girl-animated-v2.glb',use_selection=True,use_visible=True,use_renderable=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_frame_range=False,export_force_sampling=True,export_skins=True,export_morph=False,export_yup=True,export_all_influences=False)
print(json.dumps(report,ensure_ascii=False))
