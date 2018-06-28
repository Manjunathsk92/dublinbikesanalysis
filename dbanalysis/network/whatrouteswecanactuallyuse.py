import os
import pickle
base_dir = '/home/student/data/stops/'
with open('/home/student/dbanalysis/dbanalysis/resources/dep_times.pickle','rb') as handle:
    dep_times = pickle.load(handle)
total=0
dropped = 0
output={}
for route in dep_times:
    vs =[]
    for variation in dep_times[route]:
        broken = False
        total +=1
        v=variation['pattern']
        for i in range(0, len(v)-1):
            if not os.path.isdir(base_dir + v[i]) or not os.path.exists(base_dir+v[i]+'/'+v[i+1]+'.csv'):
                dropped+=1
                broken=True
                break
        if not broken:
            vs.append(variation)

    if vs != []:
        output[route] = vs

print(total)
print(dropped)
with open('routeswecanuse.pickle','wb') as handle:
    pickle.dump(output,handle,protocol=pickle.HIGHEST_PROTOCOL)

print('done')
            
            
        
        

    
