from math import inf
class network():


    def __init__(self):
        import json
        from dbanalysis.classes import simple_stop as stop
        from dbanalysis.classes import router
        from dbanalysis.classes.time_tabler_refac import time_tabler
        from dbanalysis.stop_tools import stop_finder,stop_getter
        self.stop_finder = stop_finder()
        self.s_getter = stop_getter()
        self.route_info = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
        self.nodes_map = {}
        self.nodes = {}
        self.routes = {}
        self.time_tabler = time_tabler()
        #build routes first
        for route in self.route_info:
            for v_num,arr in enumerate(self.route_info[route]):
                r = router.router(route,v_num,arr)
                if r.has_model():
                    if route not in self.routes:
                        self.routes[route] = {}
                    self.routes[route][v_num] = r
                else:
                    del(r)
                #add stops to graph
                for i in range(1,len(arr) -1):
                    if str(arr[i]) not in self.nodes_map:
                        
                        self.nodes_map[str(arr[i])] = {'backlinks':[],\
                                                      'links':set([str(arr[i+1])]),\
                                                       'weight':inf,\
                                                        't':'m'}
                        self.nodes[str(arr[i])] = stop.stop(str(arr[i]),self.s_getter.get_stop_info(str(arr[i])))
                    else:
                        self.nodes_map[str(arr[i])]['links'].add(str(arr[i+1]))
                        self.nodes[str(arr[i])].add_link(str(arr[i+1]))
                    if str(arr[i+1]) not in self.nodes_map[str(arr[i])]:
                        self.nodes_map[str(arr[i+1])] = {'backlinks':[],\
                                                        'links':set(),\
                                                        'weight':inf,\
                                                        't':'m'}
                        self.nodes[str(arr[i+1])] = stop.stop(str(arr[i+1]),self.s_getter.get_stop_info(str(arr[i+1])))


    def generate_time_tables(self):
        import datetime
        import time
        count = 0
        for route in self.routes:
            can_model = False
            try: 
                d = self.time_tabler.get_dep_times_five_days(route,datetime.datetime.now())  
                
                 
                can_model = True
            except:
                print(route)
            if can_model:
                
                for v_num in self.routes[route]:
                    count+=1
                    t2=time.time()
                    
                    try: 
                        r = self.routes[route][v_num]
                        b=r.generate_all_times(d[v_num]['matrix'])
                        for stopA in b:
                         
                            self.nodes[stopA].timetable.add_times(b[stopA])
                    
                        print(count,time.time() - t2)    
                    except:
                        print(route,v_num)
                del(d)

if __name__ == '__main__':
    n = network()
    print(n.nodes_map)
    import time
    t1 = time.time()
    n.generate_time_tables()
    print(time.time() - t1)    
    import pickle
    with open('networkpickle.bin','wb') as handle:
        pickle.dump(n,handle,protocol=pickle.HIGHEST_PROTOCOL)                  
