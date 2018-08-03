import json
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
stops = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','r').read())
for route in routes:
    v_num = 0
    for variation in routes[route]:

        for i in variation[1:]:

            stop = str(i)
            if 'serves' not in stops[stop]:
                stops[stop]['serves'] = {}
            
            if route not in stops[stop]['serves']:
                stops[stop]['serves'][route] = [v_num]
            else:
                stops[stop]['serves'][route].append(v_num)
        v_num+=1
        
import pickle
with open('/home/student/dbanalysis/dbanalysis/resources/new_stops_dict.bin','wb') as handle:
    pickle.dump(stops,handle,protocol=pickle.HIGHEST_PROTOCOL)

print(stops)
 

    

