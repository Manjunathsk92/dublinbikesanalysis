"""

The class representing a stop

Needs changing to reflect different route ids (for dwell time) etc

Can also be used to build analysis of the network, by setting train_model to False and just 
using these classes as holders for their data

Will define a set of functions to generate info on that data or something. Probably. Later

Need to add support for routes


"""
from dbanalysis.classes.time_tabler_refac import stop_time_table
import pandas as pd
class stop():

    def __init__(self,stop_id,stop_info):
        self.stop_id = str(stop_id)
        self.lat = stop_info['lat']
        self.lon = stop_info['lon']
        self.timetable = stop_time_table()
        self.links = set()
        self.foot_links = []
    def add_link(self,link):
        self.links.add(link)
    def add_to_time_table(self,day,link,route,df, stop_id):
        self.timetable.add_times(df,link,route, stop_id)        
    
    def get_foot_links(self):
        import pickle
        with open('/home/student/dbanalysis/dbanalysis/resources/stop_foot_distance.pickle','rb') as handle:
            foot_stops = pickle.load(handle)
        for x in foot_stops[str(self.stop_id)]:
            self.foot_links[x[0]] = (x[1]/5)*3600
    
        del(foot_stops)
