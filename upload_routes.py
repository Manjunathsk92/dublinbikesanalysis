import os
import pandas as pd
from sqlalchemy import create_engine
routes = os.listdir('/home/student/data/routesplits')
connstring = 'mysql://'+'dublinbus'+':'+'Ucd4dogs!'+'@'+'127.0.0.1:3306'+'/researchpracticum'
engine = create_engine(connstring)
from dbanalysis import  route_tools

for route in routes:
    df = route_tools.get_munged_route_data(route)
    df['route_id']=route
    df['stopA'] = df['fromstop']
    df['stopB'] = df['tostop']
    df['plannedtime_arr_A']=df['plannedtime_arr_from']
    df['plannedtime_dep_A']=df['plannedtime_dep_from']
    df['actualtime_arr_A']=df['actualtime_arr_from']
    df['actualtime_dep_A']=df['actualtime_dep_from']
    df['plannedtime_arr_B']=df['plannedtime_arr_to']
    df['actualtime_arr_B']=df['actualtime_arr_to']
    time_format = "%d-%b-%y %H:%M:%S"
    df['dt'] = pd.to_datetime(df['dayofservice'],format=time_format)
    df['dt'] = df['dt'].dt.date
    gf = df[['dt','stopA','stopB','plannedtime_arr_A','plannedtime_dep_A','actualtime_arr_A',\
             'actualtime_dep_A','plannedtime_arr_B','actualtime_arr_B','route_id']]
    for i in range (0,10):
        if i<9:
            a = int(gf.shape[0]/10)*i
            b = int(gf.shape[0]/10)*(i+1)
            cf = gf.iloc[a:b]
        else:
            a=int(gf.shape[0]/10)*i
            cd = gf.iloc[a:]
        cf.to_sql(name='dublinBus_stop_model',con=engine, index=False, if_exists='append')
    print('uploaded route',route)
