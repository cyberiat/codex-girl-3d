"""Blender import and visual inspection: blender -b --python inspect_model.py -- model.glb"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if not args:
    raise SystemExit('Pass the downloaded GLB or FBX path after --')
source = Path(args[0]).resolve()
if not source.is_file():
    raise SystemExit(f'Model not found: {source}')
bpy.ops.wm.read_factory_settings(use_empty=True)
if source.suffix.lower() in ('.glb', '.gltf'):
    bpy.ops.import_scene.gltf(filepath=str(source))
elif source.suffix.lower() == '.fbx':
    bpy.ops.import_scene.fbx(filepath=str(source))
else:
    raise SystemExit('Expected GLB, glTF, or FBX')
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not meshes:
    raise SystemExit('The imported file has no mesh')
points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
lo = Vector([min(v[i] for v in points) for i in range(3)])
hi = Vector([max(v[i] for v in points) for i in range(3)])
center = (lo + hi) / 2
height = max(hi.z - lo.z, .001)
report = {
    'source': str(source), 'bounds': {'min': list(lo), 'max': list(hi)},
    'meshes': [{'name': o.name, 'vertices': len(o.data.vertices),
                'polygons': len(o.data.polygons),
                'materials': [m.name if m else None for m in o.data.materials],
                'vertex_groups': len(o.vertex_groups)} for o in meshes],
    'armatures': [{'name': o.name, 'bones': [b.name for b in o.data.bones]}
                   for o in bpy.context.scene.objects if o.type == 'ARMATURE'],
    'actions': [a.name for a in bpy.data.actions]
}
output = root / 'blender'
output.mkdir(exist_ok=True)
(output / 'model-inspection.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 640
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
scene.world = bpy.data.worlds.new('Inspection studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.75, .8, .85, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .65
bpy.ops.object.camera_add(location=center + Vector((0, -height * 3, height * .03)))
camera = bpy.context.object
camera.name = 'Inspection camera'
camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = height * 1.2
camera.data.clip_end = height * 20
scene.camera = camera
for name, offset, power, color in [
    ('Key', (-1, -2, 2), 450, (1, .95, .9)),
    ('Fill', (1, -1, .8), 280, (.8, .95, 1)),
    ('Rim', (0, 1, 1.8), 500, (1, 1, 1)),
]:
    bpy.ops.object.light_add(type='AREA', location=center + Vector(offset) * height)
    light = bpy.context.object
    light.name = name
    light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()
    light.data.energy = power * height * height
    light.data.shape = 'DISK'
    light.data.size = height * 1.5
    light.data.color = color
scene.view_settings.view_transform = 'Standard'
bpy.ops.wm.save_as_mainfile(filepath=str(output / 'imported-model.blend'))
scene.render.filepath = str(output / 'model-front.png')
bpy.ops.render.render(write_still=True)
print('INSPECTION_COMPLETE', json.dumps(report))
