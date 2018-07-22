
import pandas as pd
class stop_link_model():
    """
    Simple class contains two linear regression models - one for dwell time and one for travel time.

Should be able to model the time taken to get between two stops
    """
    
    def __init__(self,from_stop,to_stop,data,clf='Linear',train_test=None):
        """
        Choose the regressor (clf should be regressor sorry) used to model dwelltime and travel time.
        More regressors can be implemented as 'elif' statements.
        """
        self.train_test=train_test
        if clf not in ('neural','forest'):
            from sklearn.linear_model import LinearRegression
            self.clf = LinearRegression(fit_intercept=True)
        elif clf=='neural':
            from sklearn.neural_network import MLPRegressor
            self.clf = MLPRegressor(hidden_layer_sizes=(100,), alpha=0.0001)

        self.from_stop = from_stop
        self.to_stop = to_stop
        self.data = data
        if train_test!=None:
            if train_test == 'random':
                import numpy as np
                msk = np.random.rand(len(self.data)) < 0.8
                self.data = self.data[msk]
            elif train_test == 'year':
                self.data = self.data[self.data['year']==2016]
                
        self.buildDwellTimeModel()
        self.buildTravelModel()
        #delete data to ensure RAM efficiency
        del(self.data)

    def buildDwellTimeModel(self):
        #train a single regressor for dwell time
        target = 'actualtime_dep_from'
        features = ['actualtime_arr_from','dayofweek','month','weekend']
        self.dwell_regr = self.clf.fit(self.data[features],self.data[target])
    def buildTravelModel(self):
        #train a single regressor for travel time
        target= 'actualtime_arr_to'
        features = ['actualtime_dep_from','dayofweek','month','weekend']
        self.travel_regr=self.clf.fit(self.data[features],self.data[target])
    
    def get_time_to_next_stop(self, arrival_time, dayofweek,month,weekend):
        
        """
        Get predictions for dwell time and travel time and sum them together to get the time to the next stop"
        """
        
        index1 = ['actualtime_arr_from','dayofweek','month','weekend']
        index2 = ['actualtime_dep_from','dayofweek','month','weekend']
        row = pd.DataFrame([[arrival_time,dayofweek,month,weekend]],index=index1)
        leavetime = self.dwell_regr.predict(row)[0]
        row2 = pd.DataFrame([[leavetime,dayofweek,month,weekend]],index=index2)
        arrival_time = self.travel_regr.predict(row2)[0]
        return arrival_time
    
    def get_time_to_next_stop_multiple(self,df):
        
        """
        Same as above, but for a matrix containing multiple times.
        Returns a dataframe that can be used as a timetable.
        """
        
        df['actualtime_dep_from']=self.dwell_regr.predict(df)
        df['actualtime_arr_to'] = self.travel_regr.predict(df[['actualtime_dep_from','dayofweek','month','weekend']])
        return df[['actualtime_arr_from','actualtime_arr_to','dayofweek','month','weekend']]

        
                    
