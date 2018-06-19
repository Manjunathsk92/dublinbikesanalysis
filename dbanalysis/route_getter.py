"""

Script for accessing stored route data
Actually, we don't really need this script anymore

"""

directory = '~/ResearchPracticum/data/routesplits/'
headers = ['index','datasource','dayofservice','tripid','progrnumber','stoppointid','plannedtime_arr','plannedtime_dep','actualtime_arr','actualtime_dep','vehicleid','passengers','passengersin','passengersout','distance','suppressed','justificationid','lastupdate','note']
import pandas as pd


def getRoute(route_id, trip_id=None, dayofservice=None):
    global directory
    global headers
    df=pd.read_csv(directory+route_id,names=headers)
    if trip_id == None:
        trip_id = df.iloc[1]['tripid']

    tf = df[df['tripid']==trip_id]
    if dayofservice==None:
        dayofservice = tf.loc[1]['dayofservice']
    tf = tf[tf['dayofservice']==dayofservice]
    tf=tf.sort_values(by='actualtime_arr',axis=0)
    stps = tf['stoppointid'].unique()
    return [stop for stop in stps]

