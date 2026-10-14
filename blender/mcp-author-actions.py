import bpy, math, json
from mathutils import Vector
from bpy_extras import anim_utils
rig=bpy.data.objects['GPT_Girl_Rig']; scene=bpy.context.scene
rig.animation_data_clear()
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
rig.animation_data_create(); scene.render.fps=30
baseline={'UpperArm.L':(-2,0,6),'UpperArm.R':(-2,0,-6),'Forearm.L':(-3,0,-8),'Forearm.R':(-3,0,8)}
durations={'Idle':180,'Wave':144,'Nod':96,'Bow':150,'Happy':132,'Walk':120,'LookAround':180,'Sleep':240}
def rotkeys(name,keys):
    p=rig.pose.bones[name]
    for f,xyz in keys:
        p.rotation_euler=tuple(math.radians(a) for a in xyz)
        p.keyframe_insert('rotation_euler',frame=f,group=name)
def loc(name,keys):
    p=rig.pose.bones[name]; inv=rig.data.bones[name].matrix_local.to_3x3().inverted()
    for f,xyz in keys:
        p.location=inv @ Vector(xyz); p.keyframe_insert('location',frame=f,group=name)
def curvebag(): return anim_utils.action_get_channelbag_for_slot(rig.animation_data.action,rig.animation_data.action_slot)
def ease():
    for fc in curvebag().fcurves:
        for k in fc.keyframe_points:
            k.interpolation='BEZIER'; k.handle_left_type='AUTO_CLAMPED'; k.handle_right_type='AUTO_CLAMPED'
for name,end in durations.items():
    action=bpy.data.actions.new(name); action.use_fake_user=True; rig.animation_data.action=action
    for p in rig.pose.bones:
        p.rotation_mode='XYZ'; p.location=(0,0,0); p.scale=(1,1,1)
        r=baseline.get(p.name,(0,0,0)); rotkeys(p.name,[(0,r),(end,r)])
    loc('Root',[(0,(0,0,0)),(end,(0,0,0))]); loc('Hips',[(0,(0,0,0)),(end,(0,0,0))])
    if name=='Idle':
        rotkeys('Spine',[(0,(0,0,0)),(42,(1.6,0,-1.1)),(90,(0,0,0)),(132,(-.8,0,1.2)),(180,(0,0,0))])
        rotkeys('Chest',[(0,(0,0,0)),(48,(-1.1,1.3,.6)),(96,(0,0,0)),(140,(.6,-1.5,-.5)),(180,(0,0,0))])
        rotkeys('Head',[(0,(0,0,0)),(36,(-1.5,3,2)),(84,(.8,0,0)),(125,(-.6,-3,-1.5)),(180,(0,0,0))])
        loc('Hips',[(0,(0,0,0)),(45,(.012,0,.004)),(90,(0,0,0)),(135,(-.012,0,.003)),(180,(0,0,0))])
    elif name=='Wave':
        rotkeys('UpperArm.R',[(0,(-2,0,-6)),(12,(-5,0,-10)),(30,(-7,-5,38)),(46,(-4,-2,42)),(82,(-5,2,40)),(102,(-5,0,32)),(127,(-2,0,-7)),(144,(-2,0,-6))])
        rotkeys('Forearm.R',[(0,(-3,0,8)),(14,(-7,0,14)),(32,(-12,-5,60)),(46,(-10,1,66)),(82,(-9,-3,62)),(104,(-7,0,42)),(128,(-3,0,6)),(144,(-3,0,8))])
        rotkeys('Hand.R',[(0,(0,0,0)),(31,(8,0,-8)),(43,(15,6,20)),(57,(-12,-6,-18)),(71,(15,5,18)),(85,(-10,-4,-15)),(99,(7,0,8)),(121,(-3,0,-3)),(144,(0,0,0))])
        rotkeys('Chest',[(0,(0,0,0)),(15,(-2,4,1)),(34,(1,-5,-2)),(90,(1,-4,-1)),(125,(0,1,0)),(144,(0,0,0))])
        rotkeys('Head',[(0,(0,0,0)),(20,(-3,-7,-4)),(43,(-2,-4,4)),(87,(1,-3,3)),(128,(0,1,-1)),(144,(0,0,0))])
        loc('Hips',[(0,(0,0,0)),(32,(.022,0,0)),(96,(.018,0,0)),(130,(-.004,0,0)),(144,(0,0,0))])
    elif name=='Nod':
        rotkeys('Head',[(0,(0,0,0)),(12,(-5,0,0)),(27,(17,0,-2)),(40,(-5,1,0)),(53,(12,1,1)),(66,(-2,0,0)),(78,(3,0,0)),(96,(0,0,0))])
        rotkeys('Neck',[(0,(0,0,0)),(24,(3,0,0)),(40,(-1,0,0)),(55,(2,0,0)),(78,(0,0,0))])
        rotkeys('Chest',[(0,(0,0,0)),(30,(2,0,0)),(46,(0,0,0)),(58,(1.2,0,0)),(82,(0,0,0))])
    elif name=='Bow':
        rotkeys('Head',[(0,(0,0,0)),(14,(6,0,0)),(40,(10,0,0)),(76,(10,0,0)),(110,(-3,0,0)),(134,(1,0,0)),(150,(0,0,0))])
        rotkeys('Spine',[(0,(0,0,0)),(14,(-2,0,0)),(44,(22,0,0)),(76,(22,0,0)),(116,(-1.5,0,0)),(138,(.4,0,0)),(150,(0,0,0))])
        rotkeys('Chest',[(0,(0,0,0)),(18,(1,0,0)),(46,(12,0,0)),(78,(12,0,0)),(118,(-1,0,0)),(150,(0,0,0))])
        for side,s in [('L',1),('R',-1)]:
            rotkeys('Forearm.'+side,[(0,baseline['Forearm.'+side]),(38,(-14,0,-s*20)),(80,(-14,0,-s*20)),(122,baseline['Forearm.'+side])])
            rotkeys('Hand.'+side,[(0,(0,0,0)),(42,(-5,0,s*6)),(80,(-5,0,s*6)),(128,(0,0,0))])
        loc('Hips',[(0,(0,0,0)),(44,(0,.025,-.012)),(80,(0,.025,-.012)),(128,(0,0,0))])
    elif name=='Happy':
        loc('Root',[(0,(0,0,0)),(17,(0,0,-.035)),(34,(0,0,.115)),(48,(0,0,0)),(55,(0,0,-.022)),(72,(0,0,.08)),(87,(0,0,0)),(95,(0,0,-.012)),(110,(0,0,.006)),(132,(0,0,0))])
        rotkeys('Spine',[(0,(0,0,0)),(18,(6,0,0)),(34,(-4,0,-3)),(51,(4,0,0)),(72,(-3,0,3)),(92,(2,0,0)),(116,(0,0,0))])
        rotkeys('Head',[(0,(0,0,0)),(18,(4,0,-3)),(36,(-5,-5,5)),(57,(2,0,-2)),(75,(-4,5,-5)),(104,(1,0,1)),(132,(0,0,0))])
        for side,s in [('L',1),('R',-1)]:
            rotkeys('UpperArm.'+side,[(0,baseline['UpperArm.'+side]),(18,(-8,0,s*2)),(37,(-8,0,-s*30)),(56,(-4,0,-s*23)),(75,(-6,0,-s*34)),(99,(-3,0,-s*12)),(124,baseline['UpperArm.'+side])])
            rotkeys('Forearm.'+side,[(0,baseline['Forearm.'+side]),(25,(-8,0,-s*35)),(39,(-8,0,-s*58)),(59,(-5,0,-s*42)),(78,(-8,0,-s*55)),(107,(-3,0,-s*16)),(132,baseline['Forearm.'+side])])
            rotkeys('Hand.'+side,[(0,(0,0,0)),(38,(-8,s*8,-s*12)),(57,(4,0,s*5)),(78,(-7,-s*5,-s*10)),(116,(0,0,0))])
    elif name=='Walk':
        for f in range(0,121,10):
            ph=2*math.pi*f/60
            loc('Root',[(f,(0,0,.018*(1-math.cos(ph*2))))])
            rotkeys('Hips',[(f,(1.5*math.sin(ph*2),3*math.sin(ph),2*math.sin(ph)))])
            rotkeys('Chest',[(f,(0,-2.8*math.sin(ph),-1.3*math.sin(ph)))])
            rotkeys('Head',[(f,(-1*math.sin(ph*2),1.2*math.sin(ph),.8*math.sin(ph)))])
            for side,s in [('L',1),('R',-1)]:
                step=s*math.sin(ph); bend=max(0,-step)*15
                rotkeys('Thigh.'+side,[(f,(14*step,0,0))]); rotkeys('Shin.'+side,[(f,(-bend,0,0))]); rotkeys('Foot.'+side,[(f,(-5*step+bend*.45,0,0))])
                rotkeys('UpperArm.'+side,[(f,(-2-8*step,0,s*6))])
                rotkeys('Forearm.'+side,[(f,(-3-max(0,step)*5,0,-s*(8+5*max(0,step))))])
    elif name=='LookAround':
        rotkeys('Head',[(0,(0,0,0)),(23,(-2,-28,-4)),(56,(-2,-28,-4)),(79,(1,3,1)),(108,(-3,27,5)),(136,(-3,27,5)),(164,(1,-2,-1)),(180,(0,0,0))])
        rotkeys('Neck',[(0,(0,0,0)),(29,(0,-4,0)),(59,(0,-4,0)),(83,(0,0,0)),(114,(0,4,0)),(140,(0,4,0)),(172,(0,0,0))])
        rotkeys('Chest',[(0,(0,0,0)),(35,(0,-6,-1)),(59,(0,-6,-1)),(87,(0,0,0)),(117,(0,6,1)),(140,(0,6,1)),(176,(0,0,0))])
    elif name=='Sleep':
        rotkeys('Head',[(0,(0,0,0)),(43,(14,0,7)),(70,(23,-3,11)),(104,(20,-3,10)),(140,(24,-3,11)),(168,(21,-3,10)),(196,(22,-3,10)),(223,(-3,0,-2)),(240,(0,0,0))])
        rotkeys('Chest',[(0,(0,0,0)),(60,(5,0,1)),(102,(4.2,0,1)),(144,(5.8,0,1)),(190,(5,0,1)),(225,(-1,0,0)),(240,(0,0,0))])
        rotkeys('Neck',[(0,(0,0,0)),(61,(4,0,2)),(193,(4,0,2)),(231,(0,0,0))])
    ease()
    primary={(fc.data_path,fc.array_index):fc for fc in curvebag().fcurves}
    def angle(b,axis,f):
        fc=primary.get((f'pose.bones["{b}"].rotation_euler',axis))
        return math.degrees(fc.evaluate(max(0,min(end,f)))) if fc else 0
    def rootheight(f):
        fc=primary.get(('pose.bones["Root"].location',1)); return fc.evaluate(max(0,min(end,f))) if fc else 0
    for f in range(0,end+1,3):
        t=f/end; env=math.sin(math.pi*t)**2 if name not in ['Idle','Walk'] else 1
        phase=2*math.pi*t*(2 if name=='Walk' else 1)
        yawlag=angle('Head',1,f)-angle('Head',1,f-6)
        pitchlag=angle('Head',0,f)+angle('Chest',0,f)-angle('Head',0,f-6)-angle('Chest',0,f-6)
        gravity_pitch=sum(angle(b,0,f-3) for b in ['Spine','Chest','Neck','Head'])
        hop=(rootheight(f)-rootheight(f-4))*75
        for side,s in [('L',1),('R',-1)]:
            sway=math.sin(phase-.3*s)-math.sin(-.3*s)
            rotkeys('Hair.'+side,[(f,(env*(1.3*sway-.22*pitchlag-hop)-.35*gravity_pitch,env*(-.12*yawlag),env*(s*.9*sway-.25*yawlag)))])
            tipyaw=angle('Head',1,f)-angle('Head',1,f-10)
            rotkeys('HairTip.'+side,[(f,(env*(2.0*sway-.27*pitchlag-hop*1.2)-.20*gravity_pitch,0,env*(s*1.8*sway-.32*tipyaw)))])
            arm=angle('Forearm.'+side,2,f); lag=arm-angle('Forearm.'+side,2,f-4)
            rotkeys('Sleeve.'+side,[(f,(env*(1.5*sway-.20*lag),0,env*(-.10*arm-.18*lag)))])
        for tag,s,back in [('FrontL',1,0),('FrontR',-1,0),('BackL',1,1),('BackR',-1,1)]:
            sway=math.sin(phase-.35*s)-math.sin(-.35*s)
            step=5*math.sin(phase*2)*s if name=='Walk' else 0
            rotkeys('Skirt.'+tag,[(f,(env*(.7*sway+hop*(.6 if back else -.5)+step),0,env*s*.8*sway))])
            rotkeys('Hem.'+tag,[(f,(env*(1.5*sway+hop*(.9 if back else -.7)+step*.4),0,env*s*1.2*sway))])
    ease()
    for fc in curvebag().fcurves:
        first=fc.evaluate(0)
        for k in fc.keyframe_points:
            if abs(k.co.x-end)<.01: k.co.y=first
        fc.update()
    action['description']='Blender MCP V2: pose-to-pose acting, anticipation, holds, overshoot, delayed hair/sleeve/hem motion.'
    action['fps']=30
rig.animation_data.action=bpy.data.actions['Wave']; scene.frame_start=0; scene.frame_end=144; scene.frame_set(57)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='D:/farm/gpt-dragon/blender/GPT-Girl-V2-MCP-working.blend')
print(json.dumps({'actions':durations,'bones':len(rig.data.bones),'source':'Blender live scene via MCP'},ensure_ascii=False))
