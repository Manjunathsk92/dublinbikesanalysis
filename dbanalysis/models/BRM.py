from dbanalysis import stop_tools
import pandas as pd
class BRModel():
    """
    Big route model class
    uses the distance of a stop from first stop on a route to compute predictions lalalala
    MAPE and r2 scores are not as good as they were in the notebook
    (we achieved 0.57 r2, and 7% MAPE on the time to complete the route)
    Should look into this.

    Planned time of arrival boosts score considerably
    """
    def __init__ (self, route,variation,verbose=True,src='build',rgr='RandomForest',\
                mode='validate',features = ['distance','vappr'],use_dummies=True):
        
        import json
        self.regr_type = rgr
        self.verbose = verbose
        self.route = route
        self.use_dummies = use_dummies
        self.variation = variation
        self.routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json').read())
        self.features = features
        
        self.route_array = self.routes[route][variation][1:]
        
        if src == 'build':
            if not self.can_be_modelled():
                print('fuck')
                raise ValueError ('Missing data for modelling this route')

            self.gather_data()
            self.preprocess()
            if rgr == 'RandomForest':
                from sklearn.ensemble import RandomForestRegressor as rf
                self.rgr = rf()
            elif rgr == 'Linear':
                from sklearn.linear_model import LinearRegression as lr
                self.rgr = lr(fit_intercept=True)
            elif rgr == 'Neural':
                from sklearn.neural_network import MLPRegressor as mlpr
                self.rgr = mlpr(hidden_layer_sizes=(100,))
                del(self.routes)
                if mode == 'validate':
                    self.validate_neural_network()
                else:
                    self.build_neural_network()
    
    
    def build_neural_network(self):
        import numpy as np
        msk = np.random.rand(len(self.data)) < 0.5
        self.train = self.data[msk]
        del(msk)
        from sklearn.preprocessing import Normalizer as mms
        del(self.data)
        self.X_transformer = mms().fit(self.train[self.features])
        Y = self.train['traveltime'].values
        Y=Y.reshape(-1,1)
        self.Y_transformer = mms().fit(Y)
        X = self.X_transformer.transform(self.train[self.features])
        Y = self.Y_transformer.transform(Y)
        del(self.train)
        self.model = self.rgr.fit(X,Y)
        print('Built')




    def validate_neural_network(self):
        
        self.train = self.data[self.data['year']==2016]
        self.test = self.data[self.data['year'] == 2017]
        from sklearn.preprocessing import Normalizer as mms
        del(self.data)
        self.X_transformer = mms().fit(self.train[self.features])
        Y = self.train['traveltime'].values
        #Y=Y.reshape(-1,1)
        #self.Y_transformer = mms().fit(Y)
        X = self.X_transformer.transform(self.train[self.features])
        #Y = self.Y_transformer.transform(Y)
        del(self.train)
        self.model = self.rgr.fit(X,Y)
        del(X)
        del(Y)
        distances = sorted(self.test['distance'].unique())[1:]
        number_samples = []
        r2 = []
        mae = []
        mape = []
        from sklearn import metrics
        for i in range(0, len(distances)-1):
            test = self.test[(self.test['distance']>=distances[i]) & (self.test['distance'] < distances[i+1])]
            Y = test['traveltime']
            number_samples.append(len(test))
            X = self.X_transformer.transform(test[self.features])
            real_preds = self.model.predict(X)
            #real_preds = self.Y_transformer.inverse_transform(preds.reshape(-1,1))
            #real_preds = [i[0] for i in real_preds]
            r2_score = metrics.r2_score(Y, real_preds)
            MAE = metrics.mean_absolute_error(Y,real_preds)
            MAPE = ((abs(Y - real_preds)/Y)*100).mean()
            r2.append(r2_score)
            mae.append(MAE)
            mape.append(MAPE)
            print(r2_score,MAE,MAPE)
        self.distances = distances[:-1]
        del(self.test)
        del(test)
        del(preds)        
    def build_model():
        import numpy as np
        if self.verbose:
            print('building model')
        #how many rows are we going to train on. Here we just randomly pick 50% of the samples and use that. Full df is probably too large
        msk = np.random.rand(len(self.data)) < 0.5
        self.data = self.data[msk]
        del(msk)
        self.model = self.rgr.predict(self.data[features].values,self.data[msk].values)
        del(self.data)
    def dump_model(self):
        import pickle
        import time
        t = int(time.time())
        name = str(self.route) + '_' + str(self.variation) + '_' + str(time.time()) +'.bin'
        with open('/data/BRModels/models/'+name,'wb') as handle:
            pickle.dump(self,handle,protocol = pickle.HIGHEST_PROTOCOL) 
        print('Saved Model')
    def predict(self,X):
        return self.model.predict(X)



    def gather_data(self):
        if self.verbose:
            print('gathering data...')
        from dbanalysis import stop_tools
        arr = self.route_array
        import os
        to_concat = []
        for i in range(len(arr)-1):
            
            data = stop_tools.get_stop_link(arr[i],arr[i+1])
            if data is not None:
                
            
                routeids = data['routeid'].unique()
                valid_routeids = [r for r in routeids if r.split('_')[0] == self.route]
                data = data[data['routeid'].isin(valid_routeids)]

                to_concat.append(data)
            
            del(data)
        self.data = pd.concat(to_concat,axis=0)
        del to_concat
        

    def preprocess(self):
        if self.verbose:
            print('Preprocessing data')
        self.select_routes()
        self.clean_1()
        self.add_distances()
        
        self.add_base_departure_time()
        self.add_time_info()
        self.merge_weather()
        if self.use_dummies:
            self.add_dummies()
            self.features += self.dummy_features
        self.data=self.data[self.data['traveltime']>0]
        self.data['planned_traveltime'] = self.data['plannedtime_arr_from'] - self.data['base_time_dep']
    def select_routes(self):
        if self.verbose:
            print('parsing routeids')
        routeids = self.data['routeid'].unique()
        valid_routeids = [r for r in routeids if r.split('_')[0] == self.route]
        self.data = self.data[self.data['routeid'].isin(valid_routeids)]
    def clean_1(self):
        if self.verbose:
            print('dropping null values')
        self.data = self.data.dropna()
        
    def add_distances(self):
        if self.verbose:
            print('adding distances')
        s_getter =stop_tools.stop_getter()
        total_distance = 0
        r = self.route_array
        route_distances = {r[0]:0}
        
        for i in range(0, len(r)-1):
            distance = s_getter.get_stop_distance(str(r[i]),str(r[i+1]))
                
            total_distance += distance
            route_distances[r[i+1]]=total_distance
        self.data['distance']=self.data['stopA'].apply(lambda x: route_distances[x])
        del(s_getter)
    def add_base_departure_time(self):
        if self.verbose:
            print('adding base departure times')
       
        keys= self.data[self.data['stopA']==self.route_array[0]]
        keys['base_time_dep']=keys['actualtime_arr_from']
        keys2=keys[['tripid','dayofservice','base_time_dep']]
        self.data = pd.merge(self.data,keys2,on=['dayofservice','tripid'])
        
        self.data['traveltime']=self.data['actualtime_arr_from']-self.data['base_time_dep']        
        del(keys)
        del(keys2)
    
    def add_time_info(self):
        if self.verbose:
            print('adding time information')
        time_format = "%d-%b-%y %H:%M:%S"
        self.data['dt']=pd.to_datetime(self.data['dayofservice'],format=time_format)
        self.data['day']=self.data['dt'].dt.dayofweek
        self.data['month']=self.data['dt'].dt.month
        self.data['hour'] = self.data['base_time_dep'] //3600
        self.data['weekend']=self.data['day']>4
        self.data['year']=self.data['dt'].dt.year
        self.data['date'] = self.data['dt'].dt.date
    def merge_weather(self,weather=None):
        if self.verbose:
            print('merging weather')
        if weather == None:
          
            weather = pd.read_csv('/home/student/dbanalysis/dbanalysis/resources/cleanweather.csv').dropna()
        weather['dt']=pd.to_datetime(weather['date'])
        weather['hour']=weather['dt'].dt.hour
        weather['date']=weather['dt'].dt.date
        
        self.data = pd.merge(self.data,weather,on=['date','hour'])
        del(weather)

    def add_dummies(self):
        if self.verbose:
            print('Making dummy features')
        self.data = pd.get_dummies(self.data,columns=['day','month','hour'])
        for hour in range(5,25):
            if 'hour_'+str(hour) not in self.data.columns:
                self.data['hour_'+str(hour)] = 0

        self.dummy_features = [col for col in self.data.columns\
                                if (col[0:3] == 'day' and col != 'dayofservice')\
                                or col[0:5] == 'month' or col[0:4] == 'hour']
       
    def can_be_modelled(self):
        if self.verbose:
            print('Checking for data files')
        import os
        base_dir = '/data/stops/'
        arr = self.route_array
        #if the first stop is missing, then we won't attempt to model this route
            
        if os.path.exists(base_dir+str(arr[1])+'/'+str(arr[2])+'.csv'):

            return True
        else:
            return False
if __name__=='__main__':
    import time
    t1 = time.time()
    model = BRModel('104',0,rgr='Neural',mode='build')
    t2 = time.time() - t1
    print('completed in', t2//3600, 'hours', (t2%3600)//60, 'minutes')
    import pickle
    #with open('/data/bigroutemodelneural.pickle','wb') as handle:
     #   pickle.dump(model.rgr,handle,protocol=pickle.HIGHEST_PROTOCOL)
