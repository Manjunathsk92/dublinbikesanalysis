import pandas as pd
import json

def get_trips_days(df):
    """
	For a given route dataframe, create a dictionary matching
	trip ids with their days of service

	"""
    trips_days = {}
    trips = df['tripid'].unique()
    for trip_id in trips:
        #for every trip id, find the daysofservice it refers to
        days = df[df['tripid']==trip_id]['dayofservice'].unique()
        #add this to our dictionary
        trips_days[trip_id]=[day for day in days]
        return trips_days

def get_all_routes():
	'''Return a dictionary listing 1 array for every route name. Might not be the exact route used by Dublin Bus'''
	import route_getter as r
	import os
	routes = os.listdir('/home/student/ResearchPracticum/data/routesplits/')
	dictionary = {}
	for route in routes:
		dictionary[route] = r.getRoute(route)
	return dictionary

def get_unique_routes(df):
    """
    Should find all of the unique paths that are referenced by a route id in the data. Not much use at present.
    Might be useful when we want to look at busses skipping stops.
    """
    routes={}
    df = df.sort_values(axis=0,by=['tripid','dayofservice','actualtime_arr'])
    tracking = False
    for i in df.itertuples():
        if not tracking:
            dayofservice=i[3]
            route=[i[6]]
            tracking = True
        elif dayofservice != i[3]:
            routes.add(tup1le(route))
            dayofservice=i[3]
            route=[i[6]]
        else:
            route.append(i[6])
    return routes

def map_stops_single_route(rn):
    """
    Maps stops in a route to the stops with which they share a connection
    """
    route_dict = json.loads(open('/home/student/ResearchPracticum/data/gtfs/trimmed_routes.json','r').read())[rn]
    route_dict = [route[1:] for route in route_dict]
    stops_mapped = {}
    for route in route_dict:
        for i in range(0, len(route)-1):
            if route[i] in stops_mapped:
                stops_mapped[route[i]].append(route[i+1])
            else:                                                                               stops_mapped[route[i]]=[route[i+1]]
    return stops_mapped

def map_all_stops():
    """
    Map all stops to the stops with which they share a connection
    Utilizes the function above.
    """
    stops_mapped = {}
    route_dict = json.loads(open('/home/student/ResearchPracticum/data/gtfs/trimmed_routes.json','r').read())
    for route in route_dict:
        temp_stops=(map_stops_single_route(route))
        for stop in temp_stops:
            if stop not in stops_mapped:
                stops_mapped[stop] = set([i for i in temp_stops[stop]])
            else:
                for i in temp_stops[stop]:
                    stops_mapped[stop].add(i)
    return stops_mapped

        

def get_munged_route_data(routename):
    """
    Wrangles a route.csv file into a dataframe describing the connections between stops on that route.

    Discards a portion of the data (stops that don't seem to connect to the next stop on their route). I think these discarded rows
    result from when the busses fail to stop (either the bus is too crowded, or there are no passengers to pick up or drop off). This is still speculation. It could be bad data (dublin bus just failed to record that the bus stopped, or something such).

    Would be good to edit this function to also return these missing stops (tends to be about ~10% of data). They could then be used (maybe!) to model when the bus is likely not to stop.
    """
    
    rn = routename.split('_')[0]
    stops_mapped = map_stops_single_route(rn)
    import dbanalysis.headers as hds
    headers = hds.get_route_headers()
    df = pd.read_csv('/home/student/ResearchPracticum/data/routesplits/'+routename,names=headers)
    df = df.sort_values(axis=0,by=['tripid','dayofservice','actualtime_arr'])
    tracking = False
    count=0
    data_out = []
    for row in df.itertuples():
        if not tracking and row[6] in stops_mapped:
            tracking = True
            prev_tuple = row
            prev_stop = row[6]
            prev_day = row[3]
        elif tracking:
            if row[6] in stops_mapped[prev_stop] and row[3] == prev_tuple[3] and row[4] == prev_tuple[4]:
                count+=1
                p=prev_tuple
                tp = tuple([p[3],p[4],p[6],row[6],p[7],p[8],p[9],p[10],row[7],row[9]])
                data_out.append(tp)
            prev_tuple = row
            prev_day = row[3]
            if row[6] in stops_mapped:
                prev_stop = row[6]
            else:
                tracking = False

    munged_stops = pd.DataFrame(data_out,columns = ['dayofservice','tripid','fromstop','tostop','plannedtime_arr_from',\
                                                 'plannedtime_dep_from',\
                                                'actualtime_arr_from','actualtime_dep_from',\
                                                'plannedtime_arr_to','actualtime_arr_to'])

    num_dropped_rows = df.shape[0] - munged_stops.shape[0]
    print('Dropped',num_dropped_rows,'rows')
    print('Dropped', (num_dropped_rows/df.shape[0])*100,'% of dataframe')
    return munged_stops




def get_munged_route_data_and_orphans(routename):
    """
    Same as above, but also returns a dataframe of 'oprhans' --> the stops that don't connect to the next stop on any given route.
    """
    
    rn = routename.split('_')[0]
    stops_mapped = map_stops_single_route(rn)
    import dbanalysis.headers as hds
    headers = hds.get_route_headers()
    df = pd.read_csv('/home/student/ResearchPracticum/data/routesplits/'+routename,names=headers)
    df = df.sort_values(axis=0,by=['tripid','dayofservice','actualtime_arr'])
    print(df.shape[0])
    tracking = False
    count=0
    data_out = []
    orphans = []
    for row in df.itertuples():
        if not tracking and row[6] in stops_mapped:
            tracking = True
            prev_tuple = row
            prev_stop = row[6]
            prev_day = row[3]
        elif tracking:
            if row[3] == prev_tuple[3] and row[4] == prev_tuple[4]:
                count+=1
                p=prev_tuple
                tp = tuple([p[3],p[4],p[6],row[6],p[7],p[8],p[9],p[10],row[7],row[9]])
                
                if row[6] in stops_mapped[prev_stop]:
                    data_out.append(tp)
                else:
                    orphans.append(tp)

            prev_tuple = row
            prev_day = row[3]
            if row[6] in stops_mapped:
                prev_stop = row[6]
            else:
                tracking = False

    munged_stops = pd.DataFrame(data_out,columns = ['dayofservice','tripid','fromstop','tostop','plannedtime_arr_from',\
                                                 'plannedtime_dep_from',\
                                                'actualtime_arr_from','actualtime_dep_from',\
                                                'plannedtime_arr_to','actualtime_arr_to'])
    munged_orphans = pd.DataFrame(orphans,columns=['dayofservice','tripid','fromstop','tostop','plannedtime_arr_from',\
                                                 'plannedtime_dep_from',\
                                                'actualtime_arr_from','actualtime_dep_from',\
                                                'plannedtime_arr_to','actualtime_arr_to'])
    num_dropped_rows = df.shape[0] - munged_stops.shape[0]
    print('Dropped',num_dropped_rows,'rows')
    print('Dropped', (num_dropped_rows/df.shape[0])*100,'% of dataframe')
    return munged_stops, munged_orphans

