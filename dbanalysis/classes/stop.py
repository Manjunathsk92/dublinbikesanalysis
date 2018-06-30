"""

The class representing a stop

Needs changing to reflect different route ids (for dwell time) etc

Can also be used to build analysis of the network, by setting train_model to False and just 
using these classes as holders for their data

Will define a set of functions to generate info on that data or something. Probably. Later

Need to add support for routes


"""

from dbanalysis import stop_tools as st
import os
from dbanalysis.classes.time_tabler import stop_time_table
import pandas as pd
class stop():

    def __init__(self,stop_id, coords=None, name=None, from_pickle=True, analyze=False, train_model=True):
        self.data = None
        self.cached_stats = []
        self.timetable = stop_time_table()

        if from_pickle:
            pass
        else:
            self.stop_id = stop_id
            self.stop_links = [i.split('.')[0] for i in \
                        os.listdir('/home/student/data/stops/'+str(stop_id))\
                        if i != 'orphans.csv']
        
            if coords != None and name != None:
                self.lat = coords[0]
                self.long = coords[1]
            else:
                import json
                stops_dict = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','r').read())
                self.name = stops_dict[str(stop_id)]['stop_name']
                self.lat = stops_dict[str(stop_id)]['lat']
                self.long = stops_dict[str(stop_id)]['lon']            
                del(stops_dict)
            if train_model: 
                self.train_models()
            if analyze:
                self.data = get_all_data(self)

    def add_to_time_table(self,day,link,route,df):
        self.timetable.add_times(df,link,route)        

    def get_link_data(self,link):

        return st.get_stop_link(self.stop_id,link) 
    def get_timetable(self):
        return self.timetable
            
        self.timetable[date][time] = {'route':route,'next_stop':next_stop}
    def get_all_data(self):
        """
        Retrieve all data about this stop
        """
        to_concat = []
        import pandas as pd
        for link in self.stop_links:
            to_concat.append(self.get_link_data(link))
        return self.prep_data(pd.concat(to_concat, axis=0))
    
    def prep_data(self,df,merge_weather=False,weather=None):
        """
        Prepare that data for modelling.
        Add functions here for weather, I think.
        """
        df['traveltime']=df['actualtime_arr_to'] - df['actualtime_dep_from']
        df['dwelltime']=df['actualtime_dep_from']-df['actualtime_arr_from']
        time_format = "%d-%b-%y %H:%M:%S"
        df['dt']=df['dt'] = pd.to_datetime(df['dayofservice'],format=time_format)
        df['dayofweek'] = df['dt'].dt.dayofweek
        df['month'] = df['dt'].dt.month
        df['weekend']=df['dayofweek']>4
        if merge_weather:
            df['date']=df['dt'].dt.date
            df['hour']=df['actualtime_arr_from']//3600
            weather = pd.read_csv('/home/student/data/cleanweather.csv')
            weather['date']=pd.to_datetime(weather['date'])
            weather['hour']=weather['date'].dt.hour
            weather['date']=weather['date'].dt.date
            return pd.merge(df,weather, on=['date','hour'])
        else:

            return df 



    def load_models(self,picklefile):
        """
        Load a stops models from pickle files
        """
        import pickle
        from dbanalysis.classes import stop_link_model as slm
        with open(picklefile,'rb') as handle:
            self.linkmodels = pickle.load(handle)
    
    def train_models(self):
        """
        Train models for this stop. Currently, it is agnostic as to the route being modelled for
        """
        from dbanalysis.classes import stop_link_model as slm
        data = self.get_all_data()
        self.linkmodels = {}
        for link in self.stop_links:
            in_data = data[data['stopB']==link]            
            self.linkmodels[link] = slm.stop_link_model(self.stop_id, link, in_data,clf='Linear')
        del data
        del in_data
    def predict(self,day,link,route,matrix):
        """
        Return a full travel time prediction for the journeys from this stop to the next link. Also append the predictions to this stops timetable.
        """
        predicts=self.linkmodels[link].get_time_to_next_stop_multiple(matrix)
        matrix = predicts
        self.add_to_time_table(day,link,route,matrix)        
        matrix['actualtime_arr_from'] = matrix['actualtime_arr_to'] 
        return matrix[['actualtime_arr_from','dayofweek','month','weekend']]
                

    def get_distance(self,stop=None,coords=None):
        """
        Finds the distance between stops (as the crow flies)
        """
        import haversine
        if coords != None:
            return haversine.haversine((self.lat,self.long),(coords[0],coords[1]))
        elif stop != None:
            stops_dict = json.loads(open('/home/student/dbanalysis/stops_trimmed.json','r').read())
            if stop not in stop_dict:
                print('error - invalid stop')
                return None
            else:
                lat = stop_dict[stop]['lat']
                lon = stop_dict[stop]['lon']
                return haversine.haversine((self.lat,self.long),(lat,lon))

        else:
            print('error. No data specified')
            return None
        
    def get_links(self):        
        return self.stop_links
    
    def get_basic_info(self,df,link):
        """
        Gets some basic stats about this stop, as long as its dataframe is supplied
        """
        out={}
        out['avg_travel_time']=df['traveltime'].mean()
        out['avg_dwell_time_all_routes']=df['dwelltime'].mean()
        out['link_distance'] = self.get_distance(stop=link)
        out['avg_speed'] = out['link_distance'] / out['avg_travel_time']
        out['avg_lateness'] = (df['actualtime_arr_to'] - df['actualtime_dep_from']).mean()
        return out
    def get_basic_info_link(self,link):
        return self.get_basic_info(self.data[self.data['tostop']==link],link)

    def get_basic_link_info_by_day(self,link,day):
        return self.get_basic_info(self.data[self.data['tostop']==link & self.data['dayofweek'] == day],link)
    def get_basic_link_info_by_hour(self,link,hour):
        
        return self.get_basic_info(self.data[self.data['tostop']==link & self.data['hour'] == hour],link)
    
    def get_basic_link_info_by_day_hour(self,link,day,hour):
        return self.get_basic_info(self.data[self.data['tostop']==link & self.data['dayofweek'] == day & self.data['hour']==hour],link)

    def get_basic_info_all_links(self):
        
        out = []
        for link in self.stop_links:
            out[link] = self.get_basic_info_link(link)
        return out

    def get_avg_dwell_time(self):
        return self.data['dwelltime'].mean()
    
    def clear_data(self):
        del(self.data)

    def clear_cache(self):
        del(self.cached_data)
        self.cached_data = None

    
