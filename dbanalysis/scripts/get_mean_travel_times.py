import os
import pickle
import pandas as pd
from dbanalysis.stop_tools import stop_getter
import pandas as pd
s_getter = stop_getter()
from dbanalysis import headers as hds
base_dir = '/home/student/data/stops'
time_format = "%d-%b-%y %H:%M:%S"
directories = os.listdir(base_dir)
d={}
count = 0
for stopA in directories:
    d[stopA]={}
    files = [file for file in os.listdir(base_dir+'/'+stopA) if file != 'oprhans.csv']
    for sB in files:
        count+=1
        print(count)
        if count % 100 == 0:
            print(count)
        stopB = sB.split('.')[0]
        d[stopA][stopB]={}
        distance=s_getter.get_stop_distance(stopA,stopB)
        
        if (not isinstance(distance,float)) and (not isinstance(distance,int)):
            
            continue
        d[stopA][stopB]['distance']=distance      
        df = pd.read_csv(base_dir+'/'+stopA+'/'+sB, names=hds.get_stop_link_headers())
        df['dt']=pd.to_datetime(df['dayofservice'],format=time_format)
        df['hour']=df['actualtime_arr_from']//3600
        
        df['day']=df['dt'].dt.dayofweek
        df['traveltime']=df['actualtime_arr_to']-df['actualtime_arr_from']
        
        #big mistake here
        
        for day in range(0,7):
            d[stopA][stopB][day]={}
            
            for hour in range(0,24):
                x=df[(df['day']==day) & (df['hour']==hour)]
                if x.shape[0]>1:
                
                    d[stopA][stopB][day][hour]=x['traveltime'].mean()
                    
                del(x)
        del(df)
import pickle
with open('/data/times.pickle','wb') as handle:
    pickle.dump(d,handle,protocol=pickle.HIGHEST_PROTOCOL)
    

                        
                        
                
                
        
        
