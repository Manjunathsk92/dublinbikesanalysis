"""
Split the route files up into a directory structure where there is a directory for each stop,
containing a .csv file for each link that stop has...

"""

from dbanalysis import route_tools as rt
from dbanalysis import headers
import pandas as pd
from subprocess import call
import json
import os
def split_route_file(route,dump_directory):
    print('Retrieving data for route:',route)
    data,orphans = rt.get_munged_route_data_and_orphans(route)
    data['routeid'] = route
    for stopA in data['fromstop'].unique():

        df1 = data[data['fromstop']==stopA]
        for stopB in df1['tostop'].unique():

            df2 = df1[df1['tostop'] == stopB]
            with open(dump_directory + '/' + stopA + '/' + stopB + '.csv', 'a') as handle:
                df2.to_csv(handle, headers=False)
    for stopA in orphans['fromstop'].unique():

        df1 = orphans[orphans['fromstop']==stopA]
        for stopB in df1['tostop'].unique():

            df2 = df1[df1['tostop'] == stopB]
            with open(dump_directory + '/' + stopA + '/orphans.csv', 'a') as handle:
                df2.to_csv(handle, headers=False)


def split_all_routes():
    #create files
    dump_directory = '/home/student/data/stops'
    call(['mkdir',dump_directory])
    stops_dict =json.loads(open('/home/student/dbanalysis/reduced-traffic-map.js','r').read())
    for stopA in stops_dict:
        call(['mkdir',dump_directory+'/'+stopA])
        call(['touch',dump_directory+'/'+stopA+'/'+'orphans.csv'])
        for stopB in stops_dict[stopA]['tostops']:
            call(['touch',dump_directory+'/'+stopA+'/'+stopB+'.csv'])
    length = len(os.listdir('/home/student/data/routesplits')
    print('directories created, press enter to start splitting')
    input()
    for route in os.listdir('/home/student/data/routesplits'):

        split_route_file(route,dump_directory)
        print('Splitting '+ route + ':', end='',flush=True)
        

if __name__ == '__main__':
    split_all_routes()

