"""

Set of functions for retrieving and analyzing stop-stop links. 

"""
import haversine
import os
import pandas as pd
def get_stop_link(stopA,stopB, src='file',merge_weather=False):
    
    """
    Retrieve the data describing the link between two stops
    """
    import os
    import pandas as pd
    from dbanalysis import headers as hds
    if src== 'file':
        if not os.path.exists('/data/stops/'+str(stopA) +'/' + str(stopB) +'.csv'):
            print('Error - stop link data not on disk')
            return None
        else:
            df=pd.read_csv('/home/student/data/stops/'+str(stopA) +'/' + str(stopB) +'.csv', names=hds.get_stop_link_headers())
            df['stopA'] = stopA
            df['stopB'] = stopB
            len_df_1 = len(df)            
    elif src=='db':
        #insert method here for grabbing data from database
        pass
 
    if merge_weather:
        #merge data with weather data .csv
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
        a= pd.merge(df,weather,on=['date','hour'])[cols]
        len_df2 = len(a)
        print(len_df_1,len_df2)
        return a

    else:
        return df
    
class stop_getter():

    """
    Class for grabbing gtfs data about stops.
    Grabs their coordinates, the stops that they link to, the shape between them.
    Can calculate the real driving distance between stops based on the stop shapes.
    """

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
            #if we have full shape coordinates for a the link, use these
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
        elif stop in self.stops_dict and link in self.stops_dict:
            #otherwise if we have the stop coordinates, use these
            a_data = self.stops_dict[stop]
            b_data = self.stops_dict[link]
            lat1=a_data['lat']
            long1 = a_data['lon']
            lat2=b_data['lat']
            long2 = b_data['lon']
            
            return haversine.haversine((lat1,long1),(lat2,long2))
        
        else:
            #otherwise just return nothing
            return None

    def get_shape(self,stop,link):
        #if we have the shape for this stop link, then return it
        #can be chained to return route shape between multiple stops
        if stop in self.stops_map and link in self.stops_map[stop]:

            return [self.get_stop_coords(stop)]+self.stops_map[stop][link]\
                        + [self.get_stop_coords(link)]
            
        else:
            return None


class stop_finder():

    """
    Class for finding the closest stops to a given {lat,lng} location.
    Uses a pickle file of nested clusters and cluster centres.
    Should add method for calculating actual distance to closest stops with google distance matrix.
    """

    def __init__(self):
        import pickle
        with open('/home/student/dbanalysis/dbanalysis/resources/stop_clusters.pickle','rb') as handle:

            self.clusters = pickle.load(handle)
        import haversine
        from math import inf
        import json
        self.stops_dict = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','rb').read())

    def find_closest_stops(self,lat,lon):
        """
        Recursively work through the clustered file until a group of stops close to the user is found.
        Should run in basically O(1) time as the nested clusters only go three or four deep.
        Distance only has to be calculated to 30 cluster centers.
        """
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
                return [{'stop_id':i,\
                'info':self.stops_dict[str(i)],\
                'distance':haversine.haversine((lat,lon),\
                 (self.stops_dict[str(i)]['lat'],\
                 self.stops_dict[str(i)]['lon']))}\
                 for i in best_group['nodes']]
            
            else:
                clusters = best_group['clusters']

    def rank_closest_stops(self,lat,lon):
        from operator import itemgetter
        cluster = self.find_closest_stops(lat,lon)
        cluster = sorted(cluster,key=itemgetter('distance'))
    
    def best_stop(self,lat,lon):
        cluster = rank_closest_stops(lat,lon)
        return cluster[0]
        

#functions for retrieving and prepping data on a random stop

def random_stop_data():
    """
    Retrieves and preps the data on a random stop.

    Weather data seems to include NaN values.
    """
    a,fromstop,tostop=random_stop_file()
    weather = pd.read_csv('/home/student/dbanalysis/dbanalysis/resources/cleanweather.csv')
    weather['dt']=pd.to_datetime(weather['date'])
    weather['hour']=weather['dt'].dt.hour
    weather['date']=weather['dt'].dt.date
    df=prep_test_stop(a,weather,fromstop,tostop)
    return df


def random_stop_file():
    import random
    stop_dirs=os.listdir('/home/student/data/stops')
    stop = random.choice(stop_dirs)
    c=os.listdir('/home/student/data/stops/'+stop)
    for i in c:
        if i != 'orphans.csv':
            return '/home/student/data/stops/'+stop+'/'+i, stop, i.split('.')[0]
    return None

def stop_data(fromstop,tostop):
    weather = pd.read_csv('/home/student/dbanalysis/dbanalysis/resources/cleanweather.csv')
    weather['dt']=pd.to_datetime(weather['date'])
    weather['hour']=weather['dt'].dt.hour
    weather['date']=weather['dt'].dt.date
    df=prep_test_stop('/data/stops/'+fromstop+'/'+tostop+'.csv',weather,fromstop,tostop)
    del weather
    return df

def prep_test_stop(filename,weather,fromstop,tostop):
    from dbanalysis import headers as hds
    s_getter = stop_getter()
    df=pd.read_csv(filename,names=hds.get_stop_link_headers())
    df['fromstop']=fromstop
    df['tostop']=tostop
    df['traveltime']=df['actualtime_arr_to']-df['actualtime_dep_from']
    df['dwelltime']=df['actualtime_dep_from']-df['actualtime_arr_from']
    df['distance'] = s_getter.get_stop_distance(fromstop,tostop)
    df['speed'] = df['distance'] / (df['traveltime']/3600)
   
    df['dt']=pd.to_datetime(df['dayofservice'],format= "%d-%b-%y %H:%M:%S")
    df['date']=df['dt'].dt.date
    df['day'] = df['dt'].dt.dayofweek 
    df['month'] = df['dt'].dt.month
    df['hour']=df['actualtime_arr_from']//3600
    df['year'] = df['dt'].dt.year
    weather.drop('dt', axis=1,inplace=True)
    df = pd.merge(df,weather, on=['date','hour'])
    del weather
    del s_getter
    return df.dropna()

def prep_test_stop_no_weather(filename,fromstop,tostop):
    from dbanalysis import headers as hds
    df['fromstop']=fromstop
    df['tostop']=tostop
    df['traveltime']=df['actualtime_arr_to']-df['actualtime_dep_from']
    df['dwelltime']=df['actualtime_dep_from']-df['actualtime_arr_from']
    df['distance'] = s_getter.get_stop_distance(fromstop,tostop)
    df['speed'] = df['distance'] / (df['traveltime']/3600)

    df['date']=pd.to_datetime(df['dayofservice'],format= "%d-%b-%y %H:%M:%S").dt.date
    df['hour']=df['actualtime_arr_from']//3600
    df['day'] = df['dt'].dt.dayofweek
    return df

#Method to get the travel time for missing link
def get_missing_links_traveltime(prevstop, stop1, stop2, traveltime):
    if prevstop!='':
        previous_dist=stop_getter().get_stop_distance(prevstop, stop1)
        speed=previous_dist/traveltime
    else :
        # If traveltime for previous link is not available, calculate traveltime assuming a speed of 50km/hr.
        speed=0.0138
    current_link_distance=stop_getter().get_stop_distance(stop1, stop2)
    current_link_traveltime=current_link_distance/speed
    return current_link_traveltime


def fake_data_frame(route,stop1,stop2,index):
    """
    Alternative method for imputing missing stop links.
    Returns a fake dataframe
    """
    s_getter = stop_getter()
    if index == 0:
        #if the first stop in a route is missing
        # find the first existing dataframe in the route, and use that to impute the distance
        pass

    else:
        #find first previous data frame
        #find next data frame

        #if there is no previous data frame and there is a next data frame


        #if the us a previous data frame but no next data frame


        #if there is both a previous and a next dataframe


        pass






if __name__ == '__main__':
    b=stop_finder()
    print(b.find_closest_stops(53.3498,-6.2603))
