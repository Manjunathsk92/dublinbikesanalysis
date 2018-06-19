"""Splits the large leavetime files up using pandas.

Splits them into ~500 files, where each file is all of the samples that correspond to a given route id
"""
directory = input('Input the location of the csv files:')
import pandas as pd
from subprocess import call
#get the rt_trips file. This is used as a key to the leave times file
trips = pd.read_csv(directory+'rt_trips_2017_I_DB.txt', delimiter=';')
#trip id and dayofservice are a primary key to the leavetimes file, so we will
#use these to merge with the routeids in the trips files
keys=trips[['routeid','tripid','dayofservice']]
routes = [route_id for route_id in keys['routeid'].unique()]
#create a new directory, and an empty file for every route
call(['mkdir',directory+'/routesplits'])
for route_id in routes:
    call(['touch',directory+'/routesplits/'+route_id])
chunksize = 1000000
#we will read the leavetimes file 1 million rows at a time
leavetimes = pd.read_csv(directory+'rt_leavetimes_2017_I_DB.txt',delimiter=';',chunksize=1000000)
#get the headers by reading the first row  of the file
heads=leavetimes.get_chunk(1)
cols=[col for col in heads.columns]
count=0
while True:

    count+=1000000
    #read 1000000 rows of the file into a dataframe
    try:
        chunk = leavetimes.get_chunk(1000000)
    except:
        #if there are no more rows to read, then terminate
        print('Finished')
        break
    #merge this chunk with the keys in tr_trips,
    #This way we can the routeid of every row
    temp_df = pd.merge(chunk, keys, on=['tripid','dayofservice'])
    #iterate through the route ids
    for route_id in routes:
        #append all the rows that reference that route id to their corresponding file
        to_file = temp_df[temp_df['routeid']==route_id]
        with open(directory+'/routesplits/'+route_id, 'a') as f:
            to_file[cols].to_csv(f,header=False)
    print('Processed',count,'lines',end="",flush=True)
