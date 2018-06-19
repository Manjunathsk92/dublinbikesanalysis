"""

idea is to create a lateness/dwelltime/traveltime map of the data

Get the munged_data for every route, map it into a dictionary.

Every stop should reference the stops it connects to, with values for the average dwell time, average lateness, and average travel time to that connection

"""

import dbanalysis.route_tools as rt
import pandas as pd
import json
import os
import pickle
directory = '/home/student/ResearchPracticum/data/routesplits'
files = os.listdir(directory)
directory_root = directory + '/'
d={}
for route in files:

    df = rt.get_munged_route_data(route)
    df['traveltime']=df['actualtime_arr_to'] - df['actualtime_dep_from']
    df['dwelltime']=df['actualtime_dep_from'] - df['actualtime_arr_from']
    df['lateness'] = df['actualtime_arr_to'] - df['plannedtime_arr_to']
    for from_stop in df['fromstop'].unique():
        fs=str(from_stop)
        if fs not in d:
           d[fs] = {'tostops':{}, 'dwelltime':{'tot':0,'num':0}}
        
        gf = df[df['fromstop']==from_stop]
        d[fs]['dwelltime']['tot'] += sum(gf['dwelltime'])
        d[fs]['dwelltime']['num'] += gf.shape[0]
        for to_stop in gf['tostop'].unique():
            ts=str(to_stop)
            tf = gf[gf['tostop']==to_stop]
            if ts not in d[fs]['tostops']:
                d[fs]['tostops'][ts] = {'num':tf.shape[0],'trvl':sum(tf['traveltime']),'ltn':sum(tf['lateness'])}
            else:
                d[fs]['tostops'][ts]['num']+=tf.shape[0]
                d[fs]['tostops'][ts]['trvl']+=sum(tf['traveltime'])
                d[fs]['tostops'][ts]['ltn']+=sum(tf['lateness'])
        
    
with open('heatmap.pickle', 'wb') as handle:
        pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)
