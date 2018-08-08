"""

It works! It works! It kind of but not really works!

"""
import sys
stop = sys.argv[1]
from sklearn.linear_model import LinearRegression as lr
from sklearn.preprocessing import MinMaxScaler as mms
from sklearn import metrics
import pandas as pd
import json
from dbanalysis import stop_tools
import pickle
import time
t1=time.time()
with open('/data/chained_models.bin','rb') as handle:
    models = pickle.load(handle)
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
route = routes['15'][1][1:]
begins = stop_tools.stop_data(str(route[0]),str(route[1]))
ends = stop_tools.stop_data(str(route[int(stop)]),str(route[int(stop)+1]))
ends['end'] = ends['actualtime_arr_to']
merged = pd.merge(begins,ends[['tripid','dayofservice','routeid','end']], on=['tripid','dayofservice','routeid'])
features = ['rain','temp','vappr']
new_features = []
all_dummies = []
arr = []
import copy
#for i in range(0,25):
#    all_dummies.append('hour'+'_'+str(i))
for i in range(0,7):
    all_dummies.append('day'+'_'+str(i))

features = [i for i in all_dummies] + ['rain','temp','vappr','hour','hour2','hour3','hour4']
df = pd.get_dummies(merged,columns = ['day'])
for i in range(2,5):
    df['hour'+str(i)] = df['hour']**i
t1 = time.time()

for i in all_dummies:
    if i not in df.columns:

        df[i] = 0

index = 0
cur_stop = route[index]
for model in models:
    index+=1
    cur_stop = route[index]
    if cur_stop == route[int(stop)+1]:
        break
    traveltime = model.predict(df[features])
    #print(traveltime.mean()) 
    df['actualtime_arr_from'] = df['actualtime_arr_from'] + traveltime
    df = df[[i for i in df.columns if i[0:4] != 'hour']]
    df['hour'] = (df['actualtime_arr_from'] //3600).astype('int64')
    arr.append(copy.deepcopy(df))
    
    for i in range(2,5):
        df['hour'+str(i)] = df['hour'] ** i
    
print(time.time()-t1)
real_traveltimes = merged['end'] - merged['actualtime_arr_from']

pred_traveltimes = df['actualtime_arr_from'] - merged['actualtime_arr_from']
print(df['actualtime_arr_from'].mean())
print('MAE:',metrics.mean_absolute_error(real_traveltimes,pred_traveltimes))
print('MAPE:',((abs(real_traveltimes-pred_traveltimes)/real_traveltimes)*100).mean())
print('r2:',metrics.r2_score(real_traveltimes,pred_traveltimes))
print('time elapsed:',time.time()-t1)   
