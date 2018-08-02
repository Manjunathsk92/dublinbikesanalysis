import os
import pickle
from dbanalysis.models import BRM
from subprocess import call
base_directory = '/data/BRModels'
call(['mkdir',base_directory])
call(['mkdir',base_directory+'/models'])
call(['mkdir',base_directory+'/logs'])
models_directory = '/data/BRModels/models/'
logs_directory = '/data/BRModels/logs/'
import json
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json').read())
count = 0
total = 0
for route in routes:
    total += len(routes[route])
for route in routes:

    for variation in range(0, len(routes[route])):
        count +=1
        print(route,variation)
        try:
            print(count,'/',total)
        
            model = BRM.BRModel(str(route),variation,rgr='Neural',mode='build')
            with open('/data/BRM/'+str(route)+'_'+str(variation)+'.bin','wb') as handle:
                pickle.dump(model,handle,protocol=pickle.HIGHEST_PROTOCOL)
        except:
            pass
    
           
