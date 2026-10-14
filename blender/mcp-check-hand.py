import bpy, json
mesh=bpy.data.objects['GPT_Girl_Desktop_V2']; rig=bpy.data.objects['GPT_Girl_Rig']
names={g.index:g.name for g in mesh.vertex_groups}
result=[]
for zlo in [.80,.85,.90,.95,1.,1.05,1.10,1.15,1.20]:
    vs=[v for v in mesh.data.vertices if v.co.x<-.42 and zlo<=v.co.z<zlo+.05 and v.co.y<.15]
    if vs:
        sums={}
        for v in vs:
            for g in v.groups: sums[names[g.group]]=sums.get(names[g.group],0)+g.weight/len(vs)
        result.append({'z':zlo,'n':len(vs),'xrange':[min(v.co.x for v in vs),max(v.co.x for v in vs)],'yrange':[min(v.co.y for v in vs),max(v.co.y for v in vs)],'weights':sums})
print(json.dumps(result))
print('BONES',[(n,list(rig.pose.bones[n].head),list(rig.pose.bones[n].tail)) for n in ['UpperArm.R','Forearm.R','Hand.R']])
