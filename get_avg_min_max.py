import json
f=open('reduced-traffic-map.js','r').read()
d=json.loads(f)
total_stops=0
ltns =[]
trvls=[]
for i in d:

    for s in d[i]['tostops']:

        ltns.append(d[i]['tostops'][s]['ltn'])
        trvls.append(d[i]['tostops'][s]['trvl'])
        total_stops += 1

print('min lateness',min(ltns))
print('max lateness', max(ltns))
print('acg ateness', sum(ltns)/total_stops)
print('min travel time', min(trvls))
print('max travel time', max(trvls))
print('avg travel time', sum(trvls)/total_stops)


