import pandas as pd
import json 
import pickle
import pandas as pd
import numpy as np
class time_tabler():

    def __init__(self,make_schedule_keys=False):
        from dbanalysis.stop_tools import stop_getter
        self.s_getter = stop_getter()
        if make_schedule_keys:
            df = pd.read_csv('/home/student/data/gtfs/calendar.txt')
            self.schedule_keys = {}
            from dbanalysis.stop_tools import stop_getter
            self.s_getter = stop_getter()
            for s_id in df['service_id'].unique():
                G
                gf = df[df['service_id']==s_id]
                self.schedule_keys[s_id]=[i for i in gf.iloc[0,1:8].transpose()]          
            with open('/home/student/dbanalysis/dbanalysis/resources/schedule_keys.pickle','wb') as handle:
                pickle.dump(self.schedule_keys,handle,protocol=pickle.HIGHEST_PROTOCOL)

        else:
            with open('/home/student/dbanalysis/dbanalysis/resources/schedule_keys.pickle','rb') as handle:
                self.schedule_keys = pickle.load(handle)
    
        with open('/home/student/dbanalysis/dbanalysis/resources/dep_times.pickle','rb') as handle:
            self.dep_times=pickle.load(handle)
    def get_all_routes(self):
        output=[]
        for key in self.dep_times:
            output.append(key)
        return output
    
    def add_distances(self,timetables):
        """
        Multiply the size of the data frame by the number of stops. Add the distance of each stop
        To a portion of the data frame
        Facilitates quick prediction with BRModel
        """
        output = {}
        import copy
        for timetable in timetables:
            to_concat = []
            distances = []
            stopsA = []
            stopsB = []
            total_distance = 0
            for i in range(len(timetable['pattern'])-1):
                stopA = timetable['pattern'][i]
                stopB = timetable['pattern'][i+1]
                total_distance += self.s_getter.get_stop_distance(str(stopA),str(stopB))
                distances.append(total_distance)
                stopsA.append(stopA)
                stopsB.append(stopB)
            for index,distance in enumerate(distances):
                df = copy.deepcopy(timetable['matrix'])
                df['distance'] = distance
                df['stopA'] = stopsA[index]
                df['stopB'] = stopsB[index]
                to_concat.append(df)
                del(df)
            matrix = pd.concat(to_concat,axis=0)
            del(to_concat)
            output[timetable['variation']] = {'matrix':matrix,'pattern':timetable['pattern']}
        return output


            
    def get_dep_times_five_days(self,route,dt):
        """
        Generate timetables for five days at a time
        """
        day = dt.weekday()
        month = dt.month
      

        variations = self.dep_times[route]
        output = {}
        
        for index, variation in enumerate(variations):
            pattern = variation['pattern']
            times=[]
            busIDs=[]
            days = []
            temp_day = day
            for i in range(0,5):
                
                for bus_number, pair in enumerate(variation['leave_times']):
                    if self.runs_today(pair['schedule'],temp_day):
                        ts = pair['lt'].split(':')
                        total = int(ts[0])*3600 + int(ts[1]) * 60 + int(ts[2])
                        times.append(total)
                        busIDs.append(bus_number)
                        days.append(temp_day)
                temp_day += 1
                if temp_day > 6:
                    temp_day = 0
            matrix = pd.DataFrame({'actualtime_arr_from':times,'day':days,'busID':busIDs})
            matrix['month'] = month
            matrix['weekend'] = matrix['day']>4
            matrix['variation'] = index
            matrix['routeid'] = route
            matrix['hour'] = matrix['actualtime_arr_from'] // 3600
            
     
            if matrix.shape[0] > 0:
                output[index] ={'pattern':pattern,'matrix':matrix,'variation':index}
       
       
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
        for index, variation in enumerate(variations):
            pattern = variation['pattern']
            times=[]
            busIDs=[]
            for bus_number, pair in enumerate(variation['leave_times']):
                if self.runs_today(pair['schedule'],day):
                    ts = pair['lt'].split(':')
                    total = int(ts[0])*3600 + int(ts[1]) * 60 + int(ts[2])
                    times.append(total)
                    busIDs.append(bus_number)
            
            matrix = pd.DataFrame({'actualtime_arr_from':times})
            matrix['dayofweek']=day
            matrix['month'] = month
            matrix['weekend'] = weekend
            matrix['variation'] = index
            matrix['busIDs'] = busIDs
            matrix['routeid'] = route 
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
        self.has_data = [False for i in range(7)]
        self.to_concat = {}
        self.data = {}
        for i in range(7):
            self.data[i] = {}
        
       
    def add_times(self,df,link):
        
            
        if link not in self.to_concat:
            self.to_concat[link] = []
        self.to_concat[link].append(df) 
    def concat_and_sort(self):
        """
        Concat and sort data frames for each available day, and save them as raw numpy matrices.
        it is hoped that the raw numpy matrics will be faster to query
        """
        for link in self.to_concat:
            
            to_concat = self.to_concat[link]
            df = pd.concat(to_concat,axis=0)
            df=df.sort_values(by=['day','actualtime_arr_from'])
            for d in df['day'].unique():
                self.data[d][link] = df[df['day']==d][['actualtime_arr_from','actualtime_arr_to','routeid']].values
            del(df)
        del(self.to_concat)

             

    def get_next_departure(self,day,link,current_time):        
        if link not in self.data[day]:
            return None
        import numpy as np
        index=[np.searchsorted(self.data[day][link][0:,0],current_time)]
        
        if index[0] < self.data[day][link].shape[0]:
            return self.data[day][link][index]
        else:
            return None
    def get_next_route(self,day,link,route,current_time):
        import numpy as np
        index = self.data[day][link][np.searchsorted(self.data[day][link][0:,0],current_time)]
        for row in self.data[day][link][index:]:
            if row[2] == route:
                return row
        return None
      
    def get_next_departure_route(self,day,link,current_time,route):
        index = self.data[day][link][np.searchsorted(self.data[day][link][0:,0],current_time)]
        for i in self.data[day][link][index:]:
            if i[2] == route:
                return i         
        return None
    def get_time_table(self,day):
        output = []
        for link in self.data[day]:
            df = self.data[link][day]
            for row in df:
                output.append({'actualtime_arr_from':row[0],'acutaltime_arr_to':row[1],\
                            'routeid':row[2],'link':route})
        from operator import itemgetter
        return sorted(output, key=itemgetter('actualtime_arr_from')) 
        

    def add_to_database(self, df):
        """
        Need CRUD method for getting this information into a database, presumably for scaling application
        """
        
        from sqlalchemy import create_engine
       
        engine = create_engine("mysql://dublinbus:Ucd4dogs!@127.0.0.1/researchpracticum")
        con = engine.connect()
        df.to_sql(con=con, name='TimeTables', if_exists='append')
        con.close()    


if __name__ == '__main__':
    t=time_tabler()
    import datetime
    print(t.add_distances(t.get_dep_times_five_days('1',datetime.datetime.now())))
    print(t.dep_times.keys())
