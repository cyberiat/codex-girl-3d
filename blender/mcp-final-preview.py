import bpy, math, json
from mathutils import Quaternion
scene=bpy.context.scene; rig=bpy.data.objects['GPT_Girl_Rig']; mesh=bpy.data.objects['GPT_Girl_Desktop_V2']; high=bpy.data.objects['GPT_Girl_HighRes_Master']
high.hide_viewport=True; high.hide_render=True; high.hide_set(True)
rig.animation_data.action=bpy.data.actions['Wave']; scene.frame_start=0; scene.frame_end=144; scene.frame_set(42)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active; sp.region_3d.view_rotation=Quaternion((1,0,0),math.pi/2)
            sp.region_3d.view_perspective='ORTHO'; sp.region_3d.view_distance=3.6; sp.region_3d.view_location=(0,0,1)
            sp.shading.type='MATERIAL'; sp.overlay.show_overlays=False
mesh['source_asset']='Meshy_AI_Aqua_Seraphina_1014082804_texture.glb'
mesh['workflow']='Rigging and animation edited in live Blender through MCP; exported with Blender glTF.'
high['display_note']='Enable viewport monitor icon and eye to inspect full resolution; hide Desktop_V2 first.'
bpy.ops.wm.save_as_mainfile(filepath='D:/farm/gpt-dragon/blender/GPT-Girl-Desktop-Pet-V2.blend')
print(json.dumps({'file':bpy.data.filepath,'blender':bpy.app.version_string,'master_vertices':len(high.data.vertices),'master_unweighted':sum(not v.groups for v in high.data.vertices),'master_viewport_disabled':high.hide_viewport,'desktop_faces':len(mesh.data.polygons),'desktop_unweighted':sum(not v.groups for v in mesh.data.vertices),'bones':len(rig.data.bones),'actions':[a.name for a in bpy.data.actions],'mcp_addon_enabled':'blender_mcp' in bpy.context.preferences.addons}))
win=bpy.context.window_manager.windows[0]
if not win.screen.is_animation_playing:
    area=next((a for a in win.screen.areas if a.type=='VIEW_3D'),win.screen.areas[0])
    with bpy.context.temp_override(window=win,area=area): bpy.ops.screen.animation_play()
print('Animation preview playing:',win.screen.is_animation_playing)
