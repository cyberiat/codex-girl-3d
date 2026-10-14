"""Rig the user's Meshy asset and author eight reusable skeletal action clips."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/imported-model.blend'))
scene=bpy.context.scene
mesh=next(o for o in scene.objects if o.type=='MESH')
bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); bpy.context.view_layer.objects.active=mesh
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
verts=mesh.data.vertices
lo=Vector([min(v.co[i] for v in verts) for i in range(3)])
hi=Vector([max(v.co[i] for v in verts) for i in range(3)])
scale=2/(hi.z-lo.z)
for v in verts:
    v.co=(v.co-Vector(((lo.x+hi.x)/2,0,lo.z)))*scale
mesh.name='GPT_Girl_Mesh'

# The source is a single clothed surface, facing -Y in Blender. These fitted
# bones and smooth spatial weights preserve the skirt instead of splitting it.
bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
rig=bpy.context.object; rig.name='GPT_Girl_Rig'; rig.data.name='GPT_Girl_Skeleton'
rig.data.edit_bones.remove(rig.data.edit_bones[0])
spec={
 'Root':((0,0,0),(0,0,.2),None),
 'Hips':((0,0,.87),(0,0,1.1),'Root'),
 'Spine':((0,0,1.1),(0,0,1.39),'Hips'),
 'Chest':((0,0,1.39),(0,0,1.62),'Spine'),
 'Head':((0,0,1.64),(0,0,1.95),'Chest'),
 'Skirt':((0,.015,.92),(0,.015,.25),'Hips'),
}
for suffix,s in [('L',1),('R',-1)]:
    spec.update({
     'UpperArm.'+suffix:((s*.19,-.025,1.54),(s*.32,-.04,1.30),'Chest'),
     'Forearm.'+suffix:((s*.32,-.04,1.30),(s*.455,-.085,1.08),'UpperArm.'+suffix),
     'Hand.'+suffix:((s*.455,-.085,1.08),(s*.505,-.10,1.005),'Forearm.'+suffix),
     'Thigh.'+suffix:((s*.11,0,.89),(s*.12,-.01,.47),'Hips'),
     'Shin.'+suffix:((s*.12,-.01,.47),(s*.12,0,.12),'Thigh.'+suffix),
     'Foot.'+suffix:((s*.12,0,.12),(s*.12,-.14,.055),'Shin.'+suffix),
     'Hair.'+suffix:((s*.19,.14,1.69),(s*.29,.17,1.18),'Head')
    })
for name,(head,tail,parent) in spec.items():
    b=rig.data.edit_bones.new(name); b.head=head; b.tail=tail
    if parent: b.parent=rig.data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True; rig.data.display_type='STICK'
groups={name:mesh.vertex_groups.new(name=name) for name in spec}
def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a))); return t*t*(3-2*t)
def add(w,name,value):
    if value>1e-5:w[name]=w.get(name,0)+value
for v in verts:
    x,y,z=v.co; ax=abs(x); side='L' if x>=0 else 'R'
    w={}
    # Core chain, with broad blends around waist, neck, and chest.
    head=smooth(1.60,1.76,z)
    chest=smooth(1.29,1.49,z)*(1-head)
    spine=smooth(.98,1.22,z)*(1-head-chest)
    hips=1-head-chest-spine
    for n,q in [('Head',head),('Chest',chest),('Spine',spine),('Hips',hips)]:add(w,n,q)
    # Distinguish the forward sleeve/hand surface from the hair behind it.
    arm=smooth(.205,.31,ax)*(1-smooth(1.52,1.67,z))*smooth(.84,.96,z)*(1-smooth(.14,.24,y))
    if arm:
        w={k:q*(1-arm) for k,q in w.items()}
        hand=1-smooth(1.055,1.14,z)
        fore=(1-smooth(1.25,1.38,z))*(1-hand)
        for n,q in [('UpperArm',1-hand-fore),('Forearm',fore),('Hand',hand)]:add(w,n+'.'+side,arm*q)
    # Secondary hair motion is slight and limited to the rear and outer locks.
    hair=smooth(.075,.20,y)*smooth(1.04,1.23,z)*(1-smooth(1.76,1.9,z))*smooth(.12,.23,ax)*.85
    if hair:
        w={k:q*(1-hair) for k,q in w.items()};add(w,'Hair.'+side,hair)
    skirt=1-smooth(.88,1.12,z)
    if skirt:
        w={k:q*(1-skirt) for k,q in w.items()}
        # Only the visible boots receive leg weights. Cloth remains continuous.
        boot=(1-smooth(.28,.40,z))*(1-smooth(.17,.245,ax))
        add(w,'Skirt',skirt*(1-boot))
        foot=1-smooth(.10,.20,z)
        add(w,'Foot.'+side,skirt*boot*foot)
        add(w,'Shin.'+side,skirt*boot*(1-foot))
    total=sum(w.values())
    for name,value in w.items():
        if value>1e-5:groups[name].add([v.index],value/total,'REPLACE')
mesh.parent=rig
mod=mesh.modifiers.new('Soft clothing skeleton','ARMATURE');mod.object=rig
mod.use_deform_preserve_volume=True
for p in rig.pose.bones:p.rotation_mode='XYZ'
scene.render.fps=30
durations={'Idle':120,'Wave':120,'Nod':90,'Bow':120,'Happy':100,'Walk':120,'LookAround':150,'Sleep':180}
def rad(v):return math.radians(v)
def setrot(name,x=0,y=0,z=0):rig.pose.bones[name].rotation_euler=(rad(x),rad(y),rad(z))
for name,end in durations.items():
    rig.animation_data_clear()
    action=bpy.data.actions.new(name);action.use_fake_user=True
    rig.animation_data_create();rig.animation_data.action=action
    for frame in range(0,end+1,3):
        t=frame/end; phase=2*math.pi*t; envelope=math.sin(math.pi*t)**2
        for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
        setrot('Spine',x=.65*math.sin(phase));setrot('Chest',x=-.4*math.sin(phase))
        for s,sgn in [('L',1),('R',-1)]:setrot('Hair.'+s,x=.7*math.sin(phase+.3*sgn),z=.6*math.sin(phase)*sgn)
        setrot('Skirt',x=.35*math.sin(phase),z=.35*math.sin(phase))
        if name=='Wave':
            setrot('UpperArm.R',x=-5*envelope,z=12*envelope)
            setrot('Forearm.R',x=-12*envelope,z=14*envelope)
            setrot('Hand.R',x=7*math.sin(phase*3)*envelope,z=10*math.sin(phase*3)*envelope)
            setrot('Head',y=4*envelope,z=-3*envelope)
        elif name=='Nod':setrot('Head',x=9*envelope*math.sin(phase*2))
        elif name=='Bow':
            setrot('Spine',x=12*envelope);setrot('Chest',x=6*envelope);setrot('Head',x=7*envelope)
        elif name=='Happy':
            rig.pose.bones['Root'].location.z=.025*envelope*(1-math.cos(phase*3))
            setrot('Chest',z=3*envelope*math.sin(phase*2));setrot('Head',z=-4*envelope*math.sin(phase*2))
            for s,sgn in [('L',1),('R',-1)]:setrot('UpperArm.'+s,z=sgn*8*envelope)
        elif name=='Walk':
            rig.pose.bones['Root'].location.z=.008*(1-math.cos(phase*4))
            setrot('Hips',y=2*math.sin(phase*2));setrot('Skirt',x=2*math.sin(phase*2))
            for s,sgn in [('L',1),('R',-1)]:
                setrot('Thigh.'+s,x=sgn*5*math.sin(phase*2));setrot('UpperArm.'+s,x=-sgn*4*math.sin(phase*2))
        elif name=='LookAround':setrot('Head',y=18*math.sin(phase)*envelope,z=3*math.sin(phase)*envelope)
        elif name=='Sleep':
            setrot('Head',x=12*envelope,z=6*envelope);setrot('Chest',x=3*envelope)
        for p in rig.pose.bones:
            p.keyframe_insert(data_path='rotation_euler',frame=frame,group=p.name)
            if p.name=='Root':p.keyframe_insert(data_path='location',frame=frame,group=p.name)
    action['description']='Hand-authored Blender skeletal pose cycle; fitted for the Meshy dress and long hair.'
rig.animation_data.action=bpy.data.actions['Idle'];scene.frame_start=0;scene.frame_end=120;scene.frame_set(0)

# Soft neutral lighting keeps the mostly-white texture readable.
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.3
for o in scene.objects:
    if o.type=='LIGHT':o.data.energy*=.12
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
camera=scene.camera;camera.location=(0,-6,1.13);target=Vector((0,0,1.04));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=2.35
for mat in mesh.data.materials:
    bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if bs:
        for key,value in [('Metallic',0),('Roughness',.65)]:
            for link in list(bs.inputs[key].links):mat.node_tree.links.remove(link)
            bs.inputs[key].default_value=value
    mat.use_backface_culling=False
scene.render.resolution_x=640;scene.render.resolution_y=800
scene.cycles.samples=24
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/GPT-Girl-Desktop-Pet.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/gpt-girl-animated.glb'),use_selection=True,export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_frame_range=False,export_force_sampling=True,export_skins=True,export_morph=False,export_yup=True)
report={'bones':len(rig.data.bones),'vertices':len(verts),'actions':durations,'source':str(ROOT/'assets/Meshy_AI_Aqua_Seraphina_1014050452_texture.glb'),'limitations':['No separate eyelid or mouth geometry; Sleep is a dozing pose with eyes open.','Unified long dress and hair; gestures and in-place walk use conservative ranges.']}
(ROOT/'blender/animation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for name,frame in [('Idle',0),('Wave',60),('Bow',60),('Happy',48)]:
    rig.animation_data.action=bpy.data.actions[name];scene.frame_set(frame)
    scene.render.filepath=str(ROOT/'blender'/('preview-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('PET_BUILD_COMPLETE')
