"""

It works! It works! It kind of but not really works!

"""
from sklearn.linear_model import LinearRegression as lr
from sklearn.preprocessing import MinMaxScaler as mms
from sklearn import metrics
import pandas as pd
import json
from dbanalysis import stop_tools
import pickle
with open('/data/chained_models_neural.bin','rb') as handle:
    models = pickle.load(handle)
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
route = routes['15'][1][1:]
begins = stop_tools.stop_data(str(route[0]),str(route[1]))
ends = stop_tools.stop_data(str(route[-7]),str(route[-6]))
ends['end'] = ends['actualtime_arr_to']
merged = pd.merge(begins,ends[['tripid','dayofservice','routeid','end']], on=['tripid','dayofservice','routeid'])
features = ['day','month','hour','weekend','vappr']
merged['weekend'] = merged['day'] > 4
df = merged[features+['traveltime','actualtime_arr_from']]
index = 1
cur_stop = route[index]
for m in models:
    model = m['model']
    transformer = m['transformer']
    transformer2 = m['transformer2']
    index+=1
    cur_stop = route[index]
    if cur_stop == route[-6]:
        break
    X = transformer.transform(df[features])
    traveltime = model.predict(X)
    import numpy as np
    traveltime = np.array([i[0] for i in transformer2.inverse_transform(traveltime.reshape(-1,1))])
    print(traveltime.mean()) 
    df['actualtime_arr_from'] = df['actualtime_arr_from'] + traveltime
    df['hour'] = (df['actualtime_arr_from'] //3600).astype('int64')
    
   
    

real_traveltimes = merged['end'] - merged['actualtime_arr_from']

pred_traveltimes = df['actualtime_arr_from'] - merged['actualtime_arr_from']
print(df['actualtime_arr_from'].mean())
print(metrics.mean_absolute_error(real_traveltimes,pred_traveltimes))
print(metrics.r2_score(real_traveltimes,pred_traveltimes))
    
