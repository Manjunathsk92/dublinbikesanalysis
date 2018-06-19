import pickle
import json
import copy
with open('heatmap.pickle','rb') as handle:
    d=pickle.load(handle)

for fstop in d:
    
    d[fstop]['dwelltime']=d[fstop]['dwelltime']['tot'] /d[fstop]['dwelltime']['num']
    for tstop in d[fstop]['tostops']:

        a = d[fstop]['tostops'][tstop]
        a['trvl']=a['trvl']/a['num']
        a['ltn']=a['ltn']/a['num']

        d[fstop]['tostops'][tstop] = {'ltn':a['ltn'],'trvl':a['trvl']}


f=open('reduced-traffic-map.js','w')
f.write(json.dumps(d))
f.close()
