import bpy, json
from mathutils import Vector
scene = bpy.context.scene
rig = bpy.data.objects['GPT_Girl_Rig']
rig.data.pose_position = 'REST'
low = bpy.data.objects['GPT_Girl_Mesh']
low.hide_set(True)
low.hide_render = True
high = bpy.data.objects['Mesh_0']
print(json.dumps({'meshes': [{'name': o.name, 'vertices': len(o.data.vertices), 'polygons': len(o.data.polygons), 'groups': len(o.vertex_groups), 'bounds': [list(o.matrix_world @ Vector(c)) for c in o.bound_box], 'modifiers': [(m.name,m.type) for m in o.modifiers]} for o in [low,high]], 'images': [(im.name,list(im.size)) for im in bpy.data.images], 'bones': [(b.name,list(b.head_local),list(b.tail_local)) for b in rig.data.bones]}, ensure_ascii=False))
bpy.ops.wm.save_userpref()
