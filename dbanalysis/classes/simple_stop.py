"""

The class representing a stop

Needs changing to reflect different route ids (for dwell time) etc

Can also be used to build analysis of the network, by setting train_model to False and just 
using these classes as holders for their data

Will define a set of functions to generate info on that data or something. Probably. Later

Need to add support for routes


"""
import pickle
from dbanalysis.classes.time_tabler_refac import stop_time_table
import copy
import pandas as pd
from sklearn.linear_model import LinearRegression as lr
class stop():

    def __init__(self,stop_id,stop_info):
        self.stop_id = str(stop_id)
        self.lat = stop_info['lat']
        self.lon = stop_info['lon']
        self.timetable = stop_time_table()
        self.links = set()
        self.link_distances = {}
        self.foot_links = {}
        self.models = {}
    def add_link(self,link,distance):
        if link not in self.links:
            try:
                with open('/data/linear_models3/'+self.stop_id+'_'+str(link)+'.bin','rb') as handle:
                    self.models[str(link)] = pickle.load(handle)
                
                self.links.add(str(link))
                self.link_distances[link] = distance
                return True
            except Exception as e:
                print(e)
                
                print('no model for',self.stop_id,link)
                return False
        else:
            return True

    def predict_multiple(self,df,link):
        
        features = ['rain','temp','vappr','hour','hour2','hour3','hour4','day','day2','day3','day4']
        df['hour'] = df['actualtime_arr_to'] //3600
        for i in range(2,5):
            df['hour'+str(i)] = df['hour'] ** i
        
        df['actualtime_arr_from'] = df['actualtime_arr_to']
        traveltime = self.models[link].predict(df[features])
       
        if traveltime.min() <= 0:
            m = traveltime.mean()
            if m > 0:
                traveltime = m
            else:
                # add method here for just using the distance
                traveltime = 0
            
            #print(traveltime.min(),traveltime.mean())
            #print('Bad prediction for', self.stop_id,link)
            #input()
        if traveltime.max() > 500:
            #print(traveltime.max(),traveltime.mean())
            #print('Obscene prediction for',self.stop_id,link)
            #input()
            print(self.link_distances[str(link)] / (traveltime.mean()/3600),traveltime.mean())
            pass
        df['actualtime_arr_to'] = df['actualtime_arr_from'] + traveltime
        del(traveltime)
        self.add_to_time_table(link,df[['day','actualtime_arr_from','actualtime_arr_to','routeid']])
        return df 
         
            
    def add_to_time_table(self,link,df):
        self.timetable.add_times(df,link)        
    
    def single_predict(self,row,link):
        features = ['rain','temp','vappr','hour','hour2','hour3','hour4','day','day2','day3','day4']
        row['hour'] = row['actualtime_arr_to'] //3600
        for i in range(2,5):
            row['hour'+str(i)] = row['hour'] ** i
        row['actualtime_arr_from'] = row['actualtime_arr_to']
        traveltime = self.models[str(link)].predict(row[features])
        row['actualtime_arr_to'] = row['actualtime_arr_from'] + traveltime
        row['hour'] = row['actualtime_arr_to'] // 3600
        return row, traveltime 
            
    def dump_time_tables(self):
        import pickle
        with open('/home/data/timetables/'+str(self.stop_id)+'.bin','wb') as handle:
            pickle.dump(self.timetable,handle,protocol = pickle.HIGHEST_PROTOCOL)

    def get_foot_links(self):
        import pickle
        with open('/home/student/dbanalysis/dbanalysis/resources/stop_foot_distance.pickle','rb') as handle:
            foot_stops = pickle.load(handle)
        for x in foot_stops[str(self.stop_id)]:
            
            self.foot_links[x[0]] = (x[1]/5)*3600
    
        del(foot_stops)
