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
    cols = [col for col in data.columns if col not in ['fromstop','tostop']]
    for stopA in data['fromstop'].unique():
        if not os.path.isdir(dump_directory+'/'+str(stopA)):
            call(['mkdir',dump_directory+'/'+str(stopA)])
            call(['touch',dump_directory+'/'+str(stopA)+'/orphans.csv'])
        df1 = data[data['fromstop']==stopA]
        for stopB in df1['tostop'].unique():
            if not os.path.exists(dump_directory+'/'+str(stopA)+'/'+str(stopB)+'.csv'):
                call(['touch',dump_directory+'/'+str(stopA)+'/'+str(stopB)+'.csv'])

            df2 = df1[df1['tostop'] == stopB]
            with open(dump_directory + '/' + str(stopA) + '/' + str(stopB) + '.csv', 'a') as handle:
                df2[cols].to_csv(handle, header=False)
    for stopA in orphans['fromstop'].unique():
        if not os.path.isdir(dump_directory+'/'+str(stopA)):
            call(['mkdir',dump_directory+'/'+str(stopA)])
            call(['touch',dump_directory+'/'+str(stopA)+'/orphans.csv'])

        df1 = orphans[orphans['fromstop']==stopA]
        with open(dump_directory + '/' + str(stopA) + '/orphans.csv', 'a') as handle:
            df1.to_csv(handle, header=False)


def split_all_routes():
    dump_directory = '/home/student/data/stops'
    call(['mkdir',dump_directory])
    length = len(os.listdir('/home/student/data/routesplits'))
    count=0
    for route in os.listdir('/home/student/data/routesplits'):
        count+=1
        split_route_file(route,dump_directory)
        print('Splitting '+ route + ':', end='',flush=True)
        print(count,'/',length)

if __name__ == '__main__':
    split_all_routes()

