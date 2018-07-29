from dbanalysis import stop_tools
import pandas as pd
class BRModel():
    """
    Big route model class
    uses the distance of a stop from first stop on a route to compute predictions lalalala
    MAPE and r2 scores are not as good as they were in the notebook
    (we achieved 0.57 r2, and 7% MAPE on the time to complete the route)
    Should look into this.
    """
    def __init__ (self, route,variation,verbose=True,src='build',rgr='RandomForest',\
                mode='validate',features = ['base_time_dep','distance','weekend','rain','temp'],use_dummies=True):
        
        import json
        self.regr_type = rgr
        self.verbose = verbose
        self.route = route
        self.use_dummies = use_dummies
        self.variation = variation
        self.routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json').read())
        self.features = features
        self.route_array = self.routes[route][variation][1:]
        del(self.routes)
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
                self.rgr = mlpr(hidden_layer_sizes=(80,80,80,80))
                from sklearn.preprocessing import normalize
                self.X,self.norm=normalize(self.data[features+['traveltime']],axis=1,return_norm=True)

                years = self.data['year']
                distances = self.data['distance']
                traveltimes = self.data['traveltime'] 
                del(self.data)
                self.data = pd.DataFrame(self.X,columns = self.features+['traveltime'])
                self.data['norm'] = self.norm
                self.data['realtraveltime'] = traveltimes 
                self.data['distances'] = distances
                self.data['year'] = years
                self.train = self.data[self.data['year']==2016]
                self.test = self.data[self.data['year']==2017]
                del(self.data)
                self.train_X = self.train[self.features].values
                self.train_Y = self.train['traveltime'].values
                del(self.train)
                self.test_1_X = self.test[features].values
                self.test_1_Y = self.test['traveltime'].values
                self.test_2_norm = self.test[self.test['distances'] == self.test['distances'].max()]['norm']
                self.test_2_real = self.test[self.test['distances'] == self.test['distances'].max()]['realtraveltime']
                

                self.test_2_X = self.test[self.test['distances'] == self.test['distances'].max()][features].values
                self.test_2_Y = self.test[self.test['distances'] == self.test['distances'].max()]['traveltime'].values
                self.test_3_X = self.test[self.test['distances'] == self.test['distances'].median()][features].values
                self.test_3_Y = self.test[self.test['distances'] == self.test['distances'].median()]['traveltime'].values
                del(self.test)
                
                del(self.X)
                
                                

 
            if mode == 'validate':
                if self.regr_type == 'Neural':
                    self.validate_neural()
                else:
                    self.validate_model()
            elif mode == 'production':
                self.build_full_model()
                self.dump_model()
    def validate_neural(self):
        print('training regressor')
        self.model = self.rgr.fit(self.train_X,self.train_Y)
        preds = self.model.predict(self.test_1_X)
        from sklearn import metrics
        print('Validating...')
        print(metrics.r2_score(self.test_1_Y,preds))
        preds = self.model.predict(self.test_2_X)
        print(metrics.r2_score(self.test_2_Y,preds))
        print('calculated from norms-->')
        preds = preds * self.test_2_norm
        print(metrics.r2_score(self.test_2_real,preds))
        preds = self.model.predict(self.test_3_X)
        print(metrics.r2_score(self.test_3_Y,preds))
    def validate_model(self):
        self.data = self.data[self.data['traveltime']>0] 
        if self.verbose:
            print('Validating model on all trips...\n\n')
        
        self.train = self.data[self.data['year']==2016]
        self.test = self.data[self.data['year']==2017]
        self.model = self.rgr.fit(self.train_X,self.train_Y)
        preds = self.model.predict(self.test_1_X)
        from sklearn import metrics
        print('-----> Tested on all distances')
        print('R2:', metrics.r2_score(self.test_1_Y,preds))
        print('MAE:', metrics.mean_absolute_error(self.test_1_Y,preds)*self.norm[-1])
        print('MAPE:', ((abs(self.test_1_Y-preds)/self.test_1_Y)*100).mean())
        #add more options for testing eventually
        print('Validating model on longest trip')
        test2= self.test[self.test['distance']==self.test['distance'].max()]
        if self.regr_type == 'Neural':
            test2 = self.test[self.test['distance2']==self.test['distance2'].max()]
        preds = self.model.predict(test2[self.features])
        print('-----> ')
        print('R2:', metrics.r2_score(test2['traveltime'],preds))
        print('MAE:', metrics.mean_absolute_error(test2['traveltime'],preds)*self.norm[-1])
        print('MAPE:', ((abs(test2['traveltime']-preds)/test2['traveltime'])*100).mean())
        print('\n\n Validated on median trip -->')
        test2= self.test[self.test['distance']==self.test['distance'].median()]
        if self.regr_type == 'Neural':
            test2 = self.test[self.test['distance2']==self.test['distance2'].median()]
        
        preds = self.model.predict(test2[self.features])
        print('-----> ')
        print('R2:', metrics.r2_score(test2['traveltime'],preds))
        print('MAE:', metrics.mean_absolute_error(test2['traveltime'],preds)*self.norm[-1])
        print('MAPE:', ((abs(test2['traveltime']-preds)/test2['traveltime'])*100).mean())
        del(self.train)
        del(self.test)
        del(self.data)
        del(test2)


    def gather_data(self):
        if self.verbose:
            print('gathering data...')
        from dbanalysis import stop_tools
        arr = self.route_array
        import os
        to_concat = []
        for i in range(len(arr)-1):
            
            data = stop_tools.get_stop_link(arr[i],arr[i+1])
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
        self.add_time_info()
        self.add_base_departure_time()
        self.merge_weather()
        if self.use_dummies:
            self.add_dummies()
            self.features += self.dummy_features
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
        self.data['hour'] = self.data['dt'].dt.hour
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
        self.dummy_features = [col for col in self.data.columns\
                                if (col[0:3] == 'day' and col != 'dayofservice')\
                                or col[0:5] == 'month' or col[0:4] == 'hour']


    def can_be_modelled(self):
        if self.verbose:
            print('Checking for data files')
        import os
        base_dir = '/data/stops/'
        arr = self.route_array
        for i in range(len(arr)-1):
            
            if os.path.exists(base_dir+str(arr[i])+'/'+str(arr[i+1])+'.csv'):
                pass
            else:
                print('broken')
                input()
                return False
        return True
if __name__=='__main__':
    import time
    t1 = time.time()
    model = BRModel('15',2,rgr='Neural')
    t2 = time.time() - t1
    print('completed in', t2//3600, 'hours', (t2%3600)//60, 'minutes')
    import pickle
    #with open('/data/bigroutemodelneural.pickle','wb') as handle:
     #   pickle.dump(model.rgr,handle,protocol=pickle.HIGHEST_PROTOCOL)
