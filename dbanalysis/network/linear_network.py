"""

Network of bus stops, with models on the go.

"""
from dbanalysis import route_tools as rt
from dbanalysis.classes import stop as bus_stop
import json
import pickle
import os
import datetime
from dbanalysis.classes import time_tabler
class bus_network():


    def __init__(self,train=False, load_from_pickle=False,load_timetables=True):
        self.stops_dict = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','r').read())
        stops_map = rt.map_all_stops()
        self.nodes={}
        self.routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
        self.route_keys = [i.split('_')[0] for i in os.listdir('/home/student/data/routesplits')]
        self.time_tabler = time_tabler.time_tabler()
        if load_timetables:
            import pickle
            with open('/home/student/dbanalysis/dbanalysis/resources/models/tabledsimple_linear_network1530370190.1135008.pickle', 'rb') as handle:
                self.nodes = pickle.load(handle)
        elif load_from_pickle:
            import pickle
            with open('/home/student/dbanalysis/dbanalysis/resources/models/simple_linear_network1530364628.2994666.pickle', 'rb') as handle:
                self.nodes = pickle.load(handle)
        else:
            for stop in [stop for stop in self.stops_dict\
                    if os.path.isdir('/home/student/data/stops/'+str(stop))\
                    and len(os.listdir('/home/student/data/stops/'+str(stop))) > 1]:
            
                print('Modelling stop',stop)
                self.nodes[str(stop)]=(bus_stop.stop(stop,\
                                    name=self.stops_dict[str(stop)]['stop_name'],\
                                    coords=[self.stops_dict[str(stop)]['lat'],\
                                    self.stops_dict[str(stop)]['lon']]\
                                    , from_pickle = not train))
                     
            print('Only found data for', len(self.nodes) / len(stops_map), 'stops')

            self.dump_network('/home/student/dbanalysis/dbanalysis/resources/models')    
       
    def dump_network(self,directory,time_tables=False):
        """
        Save network to pickle files with timestamp
        """
        import pickle
        import time
        if time_tables:
            tabled = 'tabled'
        else:
            tabled = ''
        with open(directory+'/'+tabled+'simple_linear_network'+str(time.time())+'.pickle', 'wb') as handle:
            pickle.dump(self.nodes,handle,protocol=pickle.HIGHEST_PROTOCOL)
    
    
    def get_departure_matrices(self,route,dt):
        return self.time_tabler.get_dep_times(route,dt)
    
    def run_bus_journey(self,route, dt):
        """
        Run a bus down a route and print a set of timetables for that route.
        
        """
        year,day,month,monthday,weekend,total_time = self.prep_datetime(dt)
        for i in range(0, len(route)-1):
            stop_a_id = route[i]
            stop_b_id = route[i+1]
            model = self.nodes[str(stop_a_id)]
            total_time+=model.predict(str(stop_b_id),total_time,day,month,weekend)
            
            out_hour = int(total_time / 3600)
            out_minute = int((total_time % 3600)/60)
            out_day=datetime.datetime(year,month,monthday,out_hour,out_minute)
            print(self.stops_dict[str(stop_b_id)]['stop_name'],':',out_day)

        
    def prep_datetime(self,dt):
        """
        If a datetime isn't entered, convert it to a datetime.

        Then break the datetime down into features for the model
        """
        import datetime
        if not type(dt) is datetime.datetime:
            import datetime
            dt=datetime.datetime(dt)
        return dt.year, dt.weekday(), dt.month, dt.day, dt.day > 4, (dt.hour*3600) + (dt.minute)*60 + dt.second
    
    
    def get_links(self,stopA):
        """
        Get a list of the links that a stop has
        """
        return self.nodes[stopA].get_links()
        
    def get_stats(self,stopA,stopB,day=None,hour=None):
        """
        Get stats about a stop-stop link. Doesn't yet work.
        """
        if day == None and hour == None:
            return self.nodes[stopA].get_basic_info(stopB)
        
        elif day == None:
           return self.nodes[stopA].get_basic_link_info_by_hour(stopB,hour)

        elif hour == None:
            return self.nodes[stopA].get_basic_link_info_by_day(stopB,day)

        else:
            return self.nodes[stopA].get_basic_link_info_by_day_hour(stopB,day,hour)

    def get_all_stops(self):
        return self.stops_dict

    def get_route(self, routename, all_variations = False, variation = 0):
        try:
            if all_variations:
                return self.routes[routename]
            else:
                return self.routes[routename][variation]
        except:
            return None
    
    def get_RTPI(self,stop):
        import requests
        import json
        try:
            return json.loads(requests.get("https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid="+str(stop)+"&format=json").text)
        except:
            return None
    def generate_timetables_route(self,pattern,matrix,day,route):
        for i in range(0, len(pattern)-1):
            matrix = self.nodes[pattern[i]].predict(day,pattern[i+1],route,matrix)

    def generate_all_timetables(self,dt):
        day = dt.weekday()
        import time
        t1=time.time()
        fails=0
        routes = self.time_tabler.get_all_routes()
        print(routes)
        for route in routes:
            dept_times = self.time_tabler.get_dep_times(route,dt)
            
            for variation in dept_times:
                
                try:
                    self.generate_timetables_route(variation['pattern'],\
                                        variation['matrix'],\
                                        day,\
                                        route)
                except:
                    fails+=1
                    
        print('Generated in', time.time()-t1, 'seconds')
        print('Failed for', fails)

if __name__ == '__main__':
    import time
    b=bus_network()
    print(b.nodes['4096'].timetable.get_all_times())
