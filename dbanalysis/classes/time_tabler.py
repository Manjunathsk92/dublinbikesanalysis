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
    
        with open('/home/student/dbanalysis/dbanalysis/resources/dep_times.pickle','rb') as handle:
            self.dep_times=pickle.load(handle)
   
    def get_dep_times(self,route,day):

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
            output.append({'pattern':pattern,'times':times})
        return output
                    

    def runs_today(self,s_id,day):
        if self.schedule_keys[s_id][day]==1:
            return True
        else:
            return False
 
if __name__ == '__main__':
    t=time_tabler()
    print(t.get_dep_times('1',0))
