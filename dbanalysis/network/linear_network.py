"""

Network of bus stops, with models on the go.

"""
from dbanalysis import route_tools as rt
from dbanalysis.classes import stop as bus_stop
import json
import os
class bus_network():


    def __init__(self,train=False):
        stops_dict = json.loads(open('/home/student/dbanalysis/stops_trimmed.json','r').read())
        stops_map = rt.map_all_stops()
        self.nodes=[]
        for stop in [stop for stop in stops_map if os.path.isdir('/home/student/data/stops/'+str(stop))\
                     and len(os.listdir('/home/student/data/stops/'+str(stop))) > 1]:
            print('Modelling stop',stop)
            self.nodes.append(bus_stop.stop(stop, name=stops_dict[str(stop)]['stop_name'],\
                     coords=[stops_dict[str(stop)]['lat'],stops_dict[str(stop)]['lon']]\
                     , from_pickle = not train))
                     
        print('Only found data for', len(self.nodes) / len(stops_map), 'stops')




if __name__ == '__main__':
    import time
    t1=time.time()
    b=bus_network(train=True)
    print('Done.\n Trained linear bus network model in', time.time()-t1, 'seconds')        
