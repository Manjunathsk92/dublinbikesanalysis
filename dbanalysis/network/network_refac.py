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
        self.graph_lock = False
        self.routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
        self.route_keys = [i.split('_')[0] for i in os.listdir('/home/student/data/routesplits')]
        self.time_tabler = time_tabler.time_tabler()
        
        if load_timetables:
            #load with models built and timetables computed
            import pickle
            with open('/home/student/networkpickle', 'rb') as handle:
                self.nodes = pickle.load(handle)

        elif load_from_pickle:
            #load with models already built
            import pickle
            with open('/home/student/dbanalysis/dbanalysis/resources/models/\
            simple_linear_network1530364628.2994666.pickle', 'rb') as handle:
                self.nodes = pickle.load(handle)
        elif train:
            #load and train models
            for stop in [stop for stop in self.stops_dict\
                    if os.path.isdir('/home/student/data/stops/'+str(stop))\
                    and len(os.listdir('/home/student/data/stops/'+str(stop))) > 1]:
            
                print('Modelling stop',stop)
                self.nodes[str(stop)]=(bus_stop.stop(stop,\
                                    name=self.stops_dict[str(stop)]['stop_name'],\
                                    coords=[self.stops_dict[str(stop)]['lat'],\
                                    self.stops_dict[str(stop)]['lon']]\
                                    , from_pickle = False))
                     
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
        This method is deprecated and might not even work to be honest.
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
    
    # methods for viewing stop data. Untested. Unused, as of present. Could be worked into django api.
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
        """
        Returns dublin bus rtpi data for a stop. Employed by the django api.
        """
        import requests
        import json
        try:
            return json.loads(requests.get("https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid="+str(stop)+"&format=json").text)
        except:
            return None
    
    def generate_timetables_route(self,pattern,matrix,day,route):
        """
        Predicts and saves timetables for every stop on a given route per day
        """
        for i in range(0, len(pattern)-1):
            matrix = self.nodes[pattern[i]].predict(day,pattern[i+1],route,matrix)

    def generate_all_timetables(self,dt):
        """
        Tries to generate all timetables for a given dt
        """
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
    
    def djikstra(self,origin_Lat,origin_Lon,destination_Lat,destination_Lon,starttime=30000, text_response = True):
        origin_Lat = float(origin_Lat)
        origin_Lon = float(origin_Lon)
        starttime = float(starttime)
        if origin_Lon > 0:
            origin_Lon = origin_Lon*-1
        destination_Lat = float(destination_Lat)
        destination_Lon = float(destination_Lon)
        if destination_Lon > 0:
            destination_Lon = destination_Lon * -1
        from math import inf
        while self.graph_lock:
        #block if/while the graph is being cleared up
            pass
        self.graph_lock=True
        o_stops = [s for s in \
                    self.stop_finder.find_closest_stops(origin_Lat,origin_Lon) \
                    if s['stop_id'] in network.nodes]
        
        origin_stops = {}
        for stop in o_stops:
            stopid = stop['stop_id']
            distance = stop['distance']
            origin_stops[stopid]=distance/5

        d_stops  = [s for s in \
                    self.stop_finder.find_closest_stops(destination_Lat,destination_Lon) \
                    if s['stop_id'] in network.nodes]
        
        destination_stops = {}
        for stop in d_stops:
            stopid = stop['stop_id']
            distance=stop['distance']
            destination_stops[stopid]=distance/5
            
        for s in destination_stops:
            self.nodes[s].foot_links['end'] = destination_stops[s]
            self.nodes[s].all_links.add('end')

        for n in self.nodes:
            self.nodes[n].weight = inf
        #create dummy stop nodes for the begining and origin
        origin=dummy_stop()
        origin.weight = starttime
        origin.foot_links = origin_stops
        origin.all_links=origin_stops
        destination = dummy_stop()
        destination.weight = inf
        self.nodes['begin'] = origin
        #add the origin stop to the graph
        self.nodes['end'] = destination
        current_node = 'begin'
        current_time = starttime
        visited = []
        to_visit = []
        count=0
        heapq.heappush(to_visit,[starttime,current_node])   
        while len(to_visit) > 0 and current_node != 'end':
            node = self.nodes[current_node]
            links = self.nodes[current_node].all_links
        
            for link in links:
                if current_node != 'begin' and link in\
                    self.nodes[current_node].get_links() and\
                    hasattr(self.nodes[current_node].timetable, 'data'):        

                    try:
                        count+=1
                        resp = self.nodes[current_node].timetable.get_next_departure(link,current_time)
                   
                        if resp is None:
                            continue
                    
                        time = resp['actualtime_arr_to']
                        if time < starttime:
                            time = time + (3600 * 24)
                        route = resp['route']
                    
                        if time < self.nodes[link].weight:
                            self.nodes[link].weight = time
                            self.nodes[link].back_links.append([current_node,route,time])                   
                            heapq.heappush(to_visit,[time,link])

                    except:

                        traceback.print_exc()

                 elif link in self.nodes[current_node].foot_links:
                
                    time = self.nodes[current_node].foot_links[link] + current_time
                    if time < self.nodes[link].weight:
                        self.nodes[link].weight = time
                        #append a 'w' for route id as this is a walking link
                        self.nodes[link].back_links.append([current_node,'w',time])
                        heapq.heappush(to_visit,[time,link])
            
            #remove the next node from the bottom of the heap
            x = heapq.heappop(to_visit)
            current_time = x[0]
            current_node = x[1]

        if current_node == 'end':
        print('found end')   
        #retrace path to get the quickest route
        weight = self.nodes['end'].weight
        print(weight,starttime)
        cur_node = 'end'
        resp = [{'id':'end', 'route':'walking', 'data':\
                {'lat':destination_Lat,\
                'lon':destination_Lon,\
                'stop_name':'destination'}}]
        import json
        while weight > starttime:
            minweight = inf
            print(weight)        
            for link in self.nodes[cur_node].back_links:
                stop_id = link[0]
                if self.nodes[stop_id].weight < minweight:
                    minweight = self.nodes[stop_id].weight
                    new_curnode = stop_id
                    route = link[1]
                    if route == 'w':
                        route = 'walking'
                    weight = minweight
             
            if new_curnode != 'begin':
                resp.append({'data':self.stops_dict[new_curnode],\
                'id':new_curnode,\
                'route':route,\
                'time':weight})
            else:  
                resp.append({'id':'begin','data':\
                {'lat':origin_Lat, 'lon':origin_Lon,'stop_name':'origin'},\
                'route':'walking',\
                'time':starttime})
            cur_node = new_curnode
            weight = minweight
        if text_response:
            #put together a readable version of the response data
            text=[]
            current_route = 'walking'
            current_stop = resp[-1]
            time = current_stop['time']
            for i in range(len(resp)-2,-1,-1):
                if resp[i]['route'] != current_route:
                
                    if current_route == 'walking':
                        text.append('Walk from '+\
                                current_stop['data']['stop_name']\
                                + ' to '\
                                + resp[i]['data']['stop_name']\
                                +'.'+\
                                str((resp[i]['time']-time)//60)+\
                                ' minutes')
                    else:
                        text.append('Take the ' + current_route\
                                +' from '\
                                + current_stop['data']['stop_name']\
                                +' to '\
                                + resp[i]['data']['stop_name'] +'.'+\
                                str((resp[i]['time']-time)//60)+\
                                ' minutes')
                    current_route = resp[i]['route']
                    current_stop = resp[i]
                    time = current_stop['time']
            resp = {'data':resp,'text':text}
            
        tear_down = Thread(target=self,tear_down_dijkstra,args=(destination_stops,))
        tear_down.start()
        return resp
             
    def tear_down_dijkstra(self,destination_stops):
     #remove foot links and back links added to the graph
    #this process should trigger a seperate thread so that we can return response quicker
    
     
        self.graph_lock = True
        for stop in destination_stops:
            self.nodes[stop].foot_links.pop('end',None)
        for node in network.nodes:
            self.nodes[node].back_links = []
        self.graph_lock = False
