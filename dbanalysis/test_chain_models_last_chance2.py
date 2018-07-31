from sklearn.neural_network import MLPRegressor as mlp
from sklearn.preprocessing import MinMaxScaler as mms
from sklearn import metrics
import pandas as pd
import json
import numpy
from dbanalysis import stop_tools
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
route = routes['15'][1]
models = []
features = ['day','month','hour','weekend','vappr']
for i in range(1,len(route)-1):
    stopA = str(route[i])
    stopB = str(route[i+1])
    print('Building for',stopA,'to',stopB)
    df = stop_tools.stop_data(stopA,stopB)
    df['traveltime'] = df['actualtime_arr_to'] - df['actualtime_arr_from']
    df['weekend'] = df['day'] > 4
    print(df['traveltime'].mean())
    Y = numpy.array([i for i in df['traveltime']]).reshape(-1,1)
    transformer2 = mms().fit(Y)
    Y = transformer2.transform(Y)
    transformer1 = mms().fit(df[features])
    X = transformer1.transform(df[features])
    import numpy
    model = mlp(hidden_layer_sizes=(40,40,40)).fit(X,Y)
    models.append({'transformer':transformer1,'transformer2':transformer2,'model':model})
    del(df)
    del(X)
    del(Y)
with open('/data/chained_models_neural.bin','wb') as handle:
    import pickle
    pickle.dump(models,handle,protocol = pickle.HIGHEST_PROTOCOL)

 
