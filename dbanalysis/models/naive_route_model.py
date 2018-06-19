import pandas as pd
import json
from dbanalysis import route_tools
import os
def prep_data(route):
    
    """
    Gather and prepare the data necessary for simple route models

    """
    
    print('gathering data')
    route_names = os.listdir('/home/student/ResearchPracticum/data/routesplits')
    to_get = [r for r in route_names if r.split('_')[0] == route]
    to_concat = []
    for rt in to_get:
        to_concat.append(route_tools.get_munged_route_data(rt))
    all_stops = pd.concat(to_concat)
    print('Assigning target variables')
    all_stops['traveltime']=all_stops['actualtime_arr_to'] - all_stops['actualtime_dep_from']
    all_stops['dwelltime'] = all_stops['actualtime_dep_from'] - all_stops['actualtime_arr_from']
    print('Assigning date times')
    time_format = "%d-%b-%y %H:%M:%S"
    all_stops['dt'] = pd.to_datetime(all_stops['dayofservice'],format=time_format)
    all_stops['dayofweek']=all_stops['dt'].dt.dayofweek
    all_stops['month']=all_stops['dt'].dt.month
    all_stops['weekend']=all_stops['dayofweek']>4
    print('Done')
    return all_stops


def build_route_models(route,variant=0):
        
    """
    For a variant of a route, construct a set of models representing that route

    """

    all_stops = prep_data(route)
    from dbanalysis.classes import stop_link_model as slm
    stops_dictionary = json.loads(open('/home/student/dbanalysis/stops_trimmed.json','r').read())
    rts_dictionary = rts=json.loads(open('/home/student/dbanalysis/trimmed_routes.json','r').read())
    rt = rts_dictionary[route][variant]
    models=[]
    for i in range(1, len(rt)-1):
        fromstop = rt[i]
        tostop = rt[i+1]
        data = all_stops[(all_stops['fromstop']==fromstop) & (all_stops['tostop']==tostop)]
        stop_data = stops_dictionary[str(fromstop)]
        models.append(slm.stop_link_model(fromstop,tostop,data,stop_data,clf='neural'))
        

    return models

def route_tester(route, variant=0):

    models=build_route_models(route,variant=variant)
    stops_dictionary = json.loads(open('/home/student/dbanalysis/stops_trimmed.json','r').read())
    rts_dictionary = rts=json.loads(open('/home/student/dbanalysis/trimmed_routes.json','r').read())
    while True:
        dayofweek = int(input('Enter the day of the week (0/6):'))
        month = int(input('Enter the month (0/12):'))
        starttime = int(input('Enter the start time in seconds:'))
        beginstop = int(input('Enter the number of the begin stop: (0/'+str(len(models)-1)+')'))
        endstop = int(input('Enter the number of the end stop: ('+str(beginstop+1)+'/'+str(len(models)-1)+')'))
        weekend = dayofweek > 4
        total_time = starttime
        for model in models[beginstop:endstop+1]:
            total_time += model.get_time_to_next_stop(total_time,2,3,False)
        total_time = total_time - starttime
        print('Total time travelling from',models[beginstop].name, 'to', models[endstop].name,'was', total_time)

if __name__ == '__main__':
    route=input('Enter a route id:')
    route_tester(route)

