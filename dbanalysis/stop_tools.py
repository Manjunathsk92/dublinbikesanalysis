"""

Set of functions for retrieving and analyzing stop-stop links. 

"""


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
    

