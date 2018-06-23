"""

The class representing a stop

Needs changing to reflect different route ids (for dwell time) etc

"""

from dbanalysis import stop_tools as st
import os

class stop():

    def __init__(self,stop_id, coords=None, name=None):
            
        self.stop_id = stop_id
        self.stop_links = [i.split('.')[0] for i in \
                    os.listdir('home/student/data/stops/'+str(stop_id))\
                    if i != 'orphans.csv']
        if coords != None and name != None:
            self.lat = coords[0]
            self.long = coords[1]
        else:
            import json
            stops_dict = json.loads(f.open('home/student/dbanalysis/stops_trimmed.json','r').read())
            self.name = stop_dict[str(stop_id)]['stop_name']
            self.lat = stop_dict[str(stop_id)]['lat']
            self.long = stop_dict[str(stop_id)]['lon']            
            

    def get_link_data(self,link):

        return st.get_stop_link(stop_id,link) 

    def get_all_data(self):
        to_concat = []
        import pandas as pd
        for link in self.stop_links:
            to_concat.append(self.get_link_data(link))
        return pd.concat(to_concat, axis=0)
    
    def load_models(self,picklefile):
        import pickle
        from dbanalysis.classes import stop_link_model as slm
        with open(picklefile,'rb') as handle:
            self.linkmodels = pickle.load(handle)
    
    def train_models(self):
        from dbanalysis.classes import stop_link_model as slm
        data = self.get_all_data()
        self.linkmodels = {}
        for link in self.stop_links:
            self.linkmodels[link] = slm.stop_link_model(self.stop_id, link, data[[data['stopB']==link],clf='Linear')
        
    def predict(link,arrival_time,dayofweek,month,weekend):
        
        return self.linkmodels[link].get_time_to_next_stop(arrival_time,dayofweek,month,weekend)
                

    def get_distance(self,stop=None,coords=None):
        """
        Finds the distance between stops (as the crow flies)
        """
        import haversine
        if coords != None:
            return haversine.haversine((self.lat,self.long),(coords[0],coords[1])
        elif stop!= None:
            stops_dict = json.loads(f.open('home/student/dbanalysis/stops_trimmed.json','r').read())
            if stop not in stop_dict:
                print('error - invalid stop')
                return None
            else:
                lat = stop_dict[stop]['lat']
                lon = stop_dict[stop]['lon']
                return haversine.haversine((self.lat,self.long),(lat,lon))

        else:
            print('error. Non data specified')
            return None
        
            
