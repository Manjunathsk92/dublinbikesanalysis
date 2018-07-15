import pandas as pd
import json
import pickle
"""
Basically gets lists of stops and departure times for the network model.
There is room for some heady optimization here, data structure wise.
e.g linked lists and all of that.
Some preprocessing could be done on the times as well....

For now, the thing would be to test what routes we can't currently model for, and create a dropped version of this.. or something?

Also, we need to figure out how we're actually going to use data times and whatnot....

Should generate matrices for predictions

"""
class time_tabler():

    def __init__(self,make_schedule_keys=False):
        if make_schedule_keys:
            df = pd.read_csv('/home/student/data/gtfs/calendar.txt')
            self.schedule_keys = {}
            for s_id in df['service_id'].unique():
                
                gf = df[df['service_id']==s_id]
                self.schedule_keys[s_id]=[i for i in gf.iloc[0,1:8].transpose()]          
            with open('/home/student/dbanalysis/dbanalysis/resources/schedule_keys.pickle','wb') as handle:
                pickle.dump(self.schedule_keys,handle,protocol=pickle.HIGHEST_PROTOCOL)

        else:
            with open('/home/student/dbanalysis/dbanalysis/resources/schedule_keys.pickle','rb') as handle:
                self.schedule_keys = pickle.load(handle)
    
        with open('/home/student/dbanalysis/dbanalysis/resources/clean_routes.pickle','rb') as handle:
            self.dep_times=pickle.load(handle)
    def get_all_routes(self):
        output=[]
        for key in self.dep_times:
            output.append(key)
        return output        
    def get_dep_times(self,route,dt):
        """
        Generates departure times matrices, the inputs to chained route models.
        Output is an array of {departure time matrix, pattern} - one pattern and
        one matrix for each route variation found.
        """
        
        day = dt.weekday()
        month = dt.month
        weekend = day > 4
      

        variations = self.dep_times[route]
        output = []
        for variation in variations:
            pattern = variation['pattern']
            times=[]
            for pair in variation['leave_times']:
                if self.runs_today(pair['schedule'],day):
                    ts = pair['lt'].split(':')
                    total = int(ts[0])*3600 + int(ts[1]) * 60 + int(ts[2])
                    times.append(total)
            
            matrix = pd.DataFrame({'actualtime_arr_from':times})
            matrix['dayofweek']=day
            matrix['month'] = month
            matrix['weekend'] = weekend
            if matrix.shape[0] > 0:
                output.append({'pattern':pattern,'matrix':matrix})
        return output
                    

    def runs_today(self,s_id,day):
        """
        Checks if a given schedule id will be running on a given day.
        """
        if self.schedule_keys[s_id][day]==1:
            return True
        else:
            return False


class stop_time_table():
    """
    Simple time table dependant on pandas
    I don't think it can be scaled easily
    Currently only intended to work for a single day
    """
    def __init__(self):
        self.has_data=False
    
    def add_times(self,df,link,route):
        """
        Add bus times to this time table.
        Currently all data is stored in a singular large dataframe.
        Optimization might be possible by maintaining seperate dataframes for each route, link etc.
        """
        df['link']=link
        df['route'] = route
        if self.has_data==False:
            self.has_data=True
            self.data = df
        else:
            self.data = self.data.append(df)
        self.data=self.data.sort_values(by=['actualtime_arr_to'])
    def get_times_by_link(self,link):
        """
        Times that busses arrive for a particular link
        """
        return self.data[self.data['link']==link]
    
    def get_times_by_route(self,route):
        """
        Times busses arive for particular route
        """
        return self.data[self.data['route']==route]

    def get_next_departure(self,link,current_time):
        """
        Returns the next time a bus will get to a specified link.
        Essential to the route finding algorithm
        """
        
        a = self.data[(self.data['link']==link)\
               & (self.data['actualtime_arr_from'] >= current_time)]
        if a.shape[0]>1:
            return a.iloc[0][['actualtime_arr_to','route']]
        else:
            return None  
    
    def get_all_times(self):
        return self.data

    def drop_day(self,day):
        """
        Drop a whole day's worth of data. Presumably for when time tables are recalculated.
        """
        self.data = self.data[self.data['day']!=day]

    def add_to_database(self,day):
        """
        Need CRUD method for getting this information into a database, presumably for scaling application
        """
        pass

                 


if __name__ == '__main__':
    t=time_tabler()
    import datetime
    print(t.get_dep_times('1',datetime.datetime.now()))
