from dbanalysis.stop_tools import stop_getter
s_getter=stop_getter()
def prep_stop2(df,fromstop,tostop):
    global s_getter
    
    d=pd.DataFrame()
    d['fromstop']=[fromstop]
    d['tostop']=[tostop]
    df['traveltime']=df['actualtime_arr_to']-df['actualtime_dep_from']
    df['dwelltime']=df['actualtime_dep_from']-df['actualtime_arr_from']
    df['distance'] = s_getter.get_stop_distance(fromstop,tostop)
    df['speed'] = df['distance'] / (df['traveltime']/3600)
    df['dt'] =pd.to_datetime(df['dayofservice'],format="%d-%b-%y %H:%M:%S")
    df['day']=df['dt'].dt.dayofweek
    df['hour']=df['actualtime_arr_from']//3600
    for day in range(0,7):
        
        for hour in range(0,24):
            
            d[str(day)+'_'+str(hour)+'dwell']=df[(df['day']==day) & (df['hour']==hour)]['dwelltime'].mean()
            d[str(day)+'_'+str(hour)+'speed']=df[(df['day']==day) & (df['hour']==hour)]['speed'].mean()
        
    return d

import pandas as pd
import os
 
d={}
d['fromstop']=[]
d['tostop']=[]
for day in range(7):
    
    for hour in range(24):
        
        d[str(day)+'_'+str(hour)+'dwell']=[]
        d[str(day)+'_'+str(hour)+'speed']=[]



from dbanalysis import headers as hds
stop_dirs = os.listdir('/home/student/data/stops')
for fromstop in stop_dirs:
    
    for tostop in os.listdir('/home/student/data/stops/'+fromstop):
        
        if tostop != 'orphans.csv':
            
            ts = int(tostop.split('.')[0])
            fs=int(fromstop)
            
            df = pd.read_csv('/home/student/data/stops/'+fromstop+'/'+tostop,names=hds.get_stop_link_headers())
            df=prep_stop2(df,fs,ts)
            d['fromstop'].append(fs)
            d['tostop'].append(ts)
            for day in range(7):
    
                for hour in range(24):
        
                    d[str(day)+'_'+str(hour)+'dwell'].append(df[str(day)+'_'+str(hour)+'dwell'])
                    d[str(day)+'_'+str(hour)+'speed'].append(df[str(day)+'_'+str(hour)+'speed'])


import pickle
with open('/home/student/dbanalysis/dbanalysis/resources/dwellmatrix.pickle','wb') as handle:
    pickle.dump(d,handle,protocol=pickle.HIGHEST_PROTOCOL)
