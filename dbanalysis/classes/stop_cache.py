"""

Classes for holding statistical data about stops and stop links 

"""
import numpy as np

class stop_cache():

    def __init__(self):
        self.dict = {}
        self.keys= ['max_tt','min_tt','mean_tt','max_dw','min_dw','mean_dw']
        for key in self.keys:
            self.dict[key] = np.empty((25,8,))
            self.self.dict[key][:] = np.nan

    def set__whole_day(self, day, data):
        for key in self.keys:
            self.dict[key][24,day] = data[key]
    

    def set_whole_hour(self, hour, data):
        for key in self.keys:
            self.dict[key][hour,7] = data[key]

    
    def set_hour_day(self,hour,day,data):
        for key in self.keys:
            self.dict[key][hour,day]=data[key]
    
    def get_whole_day(self,day):

        out={}
        for key in self.keys:
            out[key] = self.dict[key][24,day]
        return out
    def get_whole_hour(self,hour):
        out={}
        for key in self.keys:
            out[key] = self.dict[key][hour,7]
        return out
    def get_hour_day(self,hour,day):

        out={}
        for key in self.keys:
            out[key] = self.dict[key][hour,day]
        return out

 
            


