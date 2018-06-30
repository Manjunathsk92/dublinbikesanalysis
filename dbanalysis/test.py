from dbanalysis.classes import time_tabler
import datetime
#testing the time tabler on three routes
tt=time_tabler.time_tabler()
dt=datetime.datetime.now()
import time
#testing building linear models for a route
route = tt.get_dep_times('15',dt)
print(route[1]['pattern'])
to_model = set()
all_routes=tt.get_all_routes()
for key in all_routes:
    route = tt.get_dep_times(key,dt)
    for r in route:
        for x in r['pattern'][:-1]:
            to_model.add(x)
    
models={}
from dbanalysis.classes import stop
t1=time.time()
for s in to_model:
    print(s)
    try:
        models[s]=stop.stop(s,from_pickle=False)
    except:
        print(stop)
print('models built in ', time.time()-t1)

all_routes=tt.get_all_routes()
#now feed the matrix into these stops...
matrix = route[1]['matrix']
import time
t1=time.time()
count=0
fails=0
for key in all_routes:
    route = tt.get_dep_times(key,dt)
    for r in route:
        try:
            matrix = r['matrix']
            for i in range(0, len(r['pattern'])-1):
                
                count+=1
                matrix = models[r['pattern'][i]].predict(0,r['pattern'][i+1],'15',matrix)
        except:
            fails+=1
        print(time.time()-t1)
print(matrix)
print(fails)
print(time.time() - t1)
