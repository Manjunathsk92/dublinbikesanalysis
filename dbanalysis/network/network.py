"""
script to make all models

Currently the running time on this is total shit

"""

src='/home/student/dbanalysis/reduced-traffic-map.js'
import json
f=open(src,'r').read()
stopdict = json.loads(f)
import time
#make all models
import pandas as pd
from sqlalchemy import create_engine
connstring = 'mysql://'+'dublinbus'+':'+'Ucd4dogs!'+'@'+'127.0.0.1:3306'+'/researchpracticum'
engine = create_engine(connstring)
from dbanalysis.classes import stop_link_model as slm
network_models = {}
for stopa in stopdict:
    network_models[stopa] = {}
    for stopb in stopdict[stopa]['tostops']:
        t1=time.time()
        query = "SELECT * FROM dublinBus_stop_model WHERE stopA="
        query += stopa
        query += " AND stopB=" + stopb+";"
       	df = pd.read_sql(con=engine,sql=query)
        print("received",df.shape[0],"rows")
        print("Took", time.time()-t1,"seconds..")
        i=input()

import pickle
with f.open('modelzzz.pickle','wb') as handle:

    pickle.dump(handle, protocol = "HIGHEST_PROTOCOL")
    print('Network created')

