from sklearn.linear_model import LinearRegression as lr
from sklearn.preprocessing import MinMaxScaler as mms
from sklearn import metrics
import pandas as pd
import json
from dbanalysis import stop_tools
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
route = routes['15'][1]
models = []
all_dummies = []

for i in range(0,25):
    all_dummies.append('hour'+'_'+str(i))
for i in range(0,7):
    all_dummies.append('day'+'_'+str(i))
for i in range(1,7):
    all_dummies.append('month'+'_'+str(i))

features = [i for i in all_dummies]
for i in range(1,len(route)-1):
    stopA = str(route[i])
    stopB = str(route[i+1])
    print('Building for',stopA,'to',stopB)
    df = stop_tools.stop_data(stopA,stopB)
    df['traveltime'] = df['actualtime_arr_to'] - df['actualtime_arr_from']
    print(df['traveltime'].mean())
    fs = ['day','hour','month']
    df = pd.get_dummies(df,columns=fs)
    for f in all_dummies:
        if f not in df.columns:
            df[f] = 0

   
    model = lr(fit_intercept=True).fit(df[features],df['traveltime'])
    models.append(model)
    del(df)

with open('/data/chained_models.bin','wb') as handle:
    import pickle
    pickle.dump(models,handle,protocol = pickle.HIGHEST_PROTOCOL)

 
