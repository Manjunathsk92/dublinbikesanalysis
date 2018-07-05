"""

Set of functions for retrieving and analyzing stop-stop links. 

"""
import haversine

def get_stop_link(stopA,stopB, src='file',merge_weather=False):
    
    """
    Retrieve the data describing the link between two stops
    """
    import os
    import pandas as pd
    from dbanalysis import headers as hds
    if src== 'file':
        if not os.path.exists('/home/student/data/stops/'+str(stopA) +'/' + str(stopB) +'.csv'):
            print('Error - stop link data not on disk')
            return None
        else:
            df=pd.read_csv('/home/student/data/stops/'+str(stopA) +'/' + str(stopB) +'.csv', names=hds.get_stop_link_headers())
            df['stopA'] = stopA
            df['stopB'] = stopB
            
    elif src=='db':
        pass
 
    if merge_weather:
        weather = pd.read_csv('/home/student/data/cleanweather.csv')
        weather['date']=pd.to_datetime(weather['date'])
        weather['hour']=weather['date'].dt.hour
        weather['date']=weather['date'].dt.date
        df['dt']=pd.to_datetime(df['dayofservice'],format="%d-%b-%y %H:%M:%S")
        df['date']=df['dt'].dt.date
        df['hour']=df['actualtime_arr_from']//3600
        
        cols=['dayofservice', 'tripid', 'plannedtime_arr_from',
       'plannedtime_dep_from', 'actualtime_arr_from', 'actualtime_dep_from',
       'plannedtime_arr_to', 'actualtime_arr_to', 'routeid', 'stopA', 'stopB','hour', 'dewpt', 'msl', 'rain', 'rhum', 'temp', 'vappr',
       'wetb']
        return pd.merge(df,weather,on=['date','hour'])[cols]

    else:
        return df
    
class stop_getter():

    def __init__(self):
        import pickle
        import json
        import haversine
        base_dir = '/home/student/dbanalysis/dbanalysis/resources/'
        with open(base_dir+'trimmed_stops_shapes_map.pickle','rb') as handle:
            self.stops_map = pickle.load(handle)

        self.stops_dict = json.loads(open(base_dir+'stops_trimmed.json','r').read())

    def get_stop_coords(self,stop):

        if stop in self.stops_dict:
           return {'lat':self.stops_dict[stop]['lat'],
                    'lon':self.stops_dict[stop]['lon']}

        else:
            return None

    def get_stop_links(self, stop):
        if stop in self.stops_map:
            return [stop for stop in self.stops_map[stop]]
        else:
            return None

    def get_stop_distance(self,stop,link):
        
        if stop in self.stops_map and link in self.stops_map[stop]:

            coords = [self.get_stop_coords(stop)] + self.stops_map[stop][link]\
                            + [self.get_stop_coords(link)]
            total_distance = 0
            for i in range(0, len(coords)-1):
                lat1 = coords[i]['lat']
                lon1=coords[i]['lon']
                lat2=coords[i+1]['lat']
                lon2=coords[i+1]['lon']
                total_distance += haversine.haversine((lat1,lon1),(lat2,lon2))
            return total_distance
        else:
            return None

    def get_shape(self,stop,link):
        if stop in self.stops_map and link in self.stops_map[stop]:

            return [self.get_stop_coords(stop)]+self.stops_map[stop][link]\
                        + [self.get_stop_coords(link)]
            
        else:
            return None


class stop_finder():

    def __init__(self):
        import pickle
        with open('/home/student/dbanalysis/dbanalysis/resources/stop_clusters.pickle','rb') as handle:

            self.clusters = pickle.load(handle)
        import haversine
        from math import inf
        import json
        self.stops_dict = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','rb').read())

    def find_closest_stops(self,lat,lon):
        from math import inf 
        clusters = self.clusters
        while True:
            min_distance=inf
            for cluster in clusters:
                
                dist=haversine.haversine((lat,lon),(cluster['lat'],cluster['lon'])) 
                if dist< min_distance:
                    min_distance = dist
                    best_group = cluster

            if 'nodes' in best_group:
                return [self.stops_dict[str(i)] for i in best_group['nodes']]
            
            else:
                clusters = best_group['clusters']

                





if __name__ == '__main__':
    b=stop_finder()
    print(b.find_closest_stops(53.498,-6.2603))
