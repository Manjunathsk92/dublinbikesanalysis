import os
from dbanalysis.models import BRModel
from subprocess import call
base_directory = '/data/BRModels'
call(['mkdir',base_directory])
call(['mkdir',base_directory+'/models'])
call(['mkdir',base_directory+'/logs'])
models_directory = '/data/BRModels/models/'
logs_directory = '/data/BRModels/logs/'
import json
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json').read())
for route in routes:

    for variation in range(0, len(routes[route])):

        model = BRM(route,variation

        
