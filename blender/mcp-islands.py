import bpy, numpy as np, json
m=bpy.data.objects['GPT_Girl_Desktop_V2'].data
n=len(m.vertices); parent=list(range(n)); sizes=[1]*n
def find(a):
    while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
    return a
for e in m.edges:
    a,b=map(find,e.vertices)
    if a!=b:
        if sizes[a]<sizes[b]: a,b=b,a
        parent[b]=a; sizes[a]+=sizes[b]
roots=[find(i) for i in range(n)]
groups={}
for i,r in enumerate(roots): groups.setdefault(r,[]).append(i)
co=np.empty(n*3,dtype=np.float32); m.vertices.foreach_get('co',co); co=co.reshape(-1,3)
atr=m.attributes.get('Surface_Island') or m.attributes.new('Surface_Island','INT','POINT'); atr.data.foreach_set('value',roots)
result=[]
for root,ids in sorted(groups.items(),key=lambda a:len(a[1]),reverse=True)[:16]:
    pts=co[ids]; result.append({'id':root,'n':len(ids),'min':pts.min(axis=0).tolist(),'max':pts.max(axis=0).tolist()})
samples=[]
for p in [(-.33,-.23,1.11),(-.35,-.05,.95),(-.49,-.22,1.01),(-.35,-.18,1.32)]:
    idx=int(np.argmin(np.sum((co-np.array(p))**2,axis=1))); samples.append({'co':co[idx].tolist(),'component':roots[idx],'n':len(groups[roots[idx]])})
print(json.dumps({'islands':len(groups),'largest':result,'samples':samples}))
