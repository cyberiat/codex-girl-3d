import bpy, numpy as np, json
mesh=bpy.data.objects['GPT_Girl_Desktop_V2']; rig=bpy.data.objects['GPT_Girl_Rig']
rig.animation_data.action=bpy.data.actions['Wave']; bpy.context.scene.frame_set(45)
bpy.context.view_layer.update()
ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()); deformed=ev.to_mesh()
n=len(mesh.data.vertices); e=len(mesh.data.edges)
rest=np.empty(n*3,dtype=np.float32); posed=np.empty(n*3,dtype=np.float32); edges=np.empty(e*2,dtype=np.int32)
mesh.data.vertices.foreach_get('co',rest); deformed.vertices.foreach_get('co',posed); mesh.data.edges.foreach_get('vertices',edges)
rest=rest.reshape(-1,3); posed=posed.reshape(-1,3); edges=edges.reshape(-1,2)
rl=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1); pl=np.linalg.norm(posed[edges[:,0]]-posed[edges[:,1]],axis=1)
strain=pl/np.maximum(rl,.002); score=np.maximum(pl-rl,0)
indices=np.argsort(score)[-20:][::-1]
names={g.index:g.name for g in mesh.vertex_groups}
print(json.dumps({'max_edge':float(pl.max()),'stretched_edges':int(np.sum((strain>3)&(pl>.03))),'worst':[{'rest_length':float(rl[i]),'posed_length':float(pl[i]),'points':[{'co':list(map(float,rest[v])),'weights':{names[g.group]:g.weight for g in mesh.data.vertices[v].groups}} for v in edges[i]]} for i in indices]}))
ev.to_mesh_clear()
