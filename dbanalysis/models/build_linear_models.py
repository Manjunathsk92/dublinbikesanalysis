import copy
    
    

def model_stop(df):
    #df = pd.get_dummies(df,columns=['day'])
    #features = ['day_'+str(i) for i in range(0,7)]
    #for f in features:
    #    if f not in df.columns:
    #        df[f] = 0
    df = df[df['traveltime'] < df['traveltime'].quantile(0.95)]
    features = ['rain','temp','vappr','hour','hour2','hour3','hour4','day','day2','day3','day4']
    for i in range(2,5):
        df['hour'+str(i)] = df['hour'] ** i
        df['day'+str(i)] = df['day'] ** i
    model = lr(fit_intercept=True).fit(df[features],df['traveltime'])
    return model,df,features 


def model_route(route,variation,v_num):
    good_data_frame = None
    good_distance = None
    global real_stops
    r_stops = []
    s_getter = stop_tools.stop_getter()
    for i in range(1, len(variation) - 1):
        stopA = str(variation[i])
        stopB = str(variation[i+1])
        if model_exists(stopA,stopB):
            if stopA in real_stops and stopB in real_stops[stopA]:
                rs = real_stops[stopA][stopB]
                good_data_frame = [rs[0],rs[1]]
                good_distance = s_getter.get_stop_distance(rs[0],rs[1])
                r_stops = [rs[0],rs[1]]
            else:
                good_data_frame = [stopA,stopB]
                good_distance = s_getter.get_stop_distance(stopA,stopB)
                r_stops = [stopA,stopB]
        else:
            
            df = stop_tools.stop_data(stopA,stopB)
            fail = False
            if df is None:
                fail = True
            elif df.shape[0] < 100:
                fail = True
            else:
                model,copy_df,features = model_stop(df)
                if not validate_model(model,copy_df,features):
                    fail = True
            
            if not fail:
                with open('/data/linear_models3/'+str(stopA)+'_'+str(stopB)+'.bin', 'wb') as handle:
                    pickle.dump(model,handle,protocol = pickle.HIGHEST_PROTOCOL)
                good_data_frame = [stopA,stopB]
                good_distance = s_getter.get_stop_distance(stopA,stopB)
                r_stops = [stopA,stopB]
                #if stopA not in real_stops:
                #    real_stops[stopA] = {}
                #if stopB not in real_stops[stopA]:
                #    real_stops[stopA][stopB] = r_stops
            else:
                #return to these routes earlier
                if good_data_frame is None:
                    return False
                else:
                    distance = s_getter.get_stop_distance(stopA,stopB)
                    # god dam error here, or not really tbh
                    if stopA not in real_stops:
                        real_stops[stopA] = {}
                    if stopB not in real_stops[stopA]:
                        real_stops[stopA][stopB] = r_stops
                        
                    df = stop_tools.stop_data(good_data_frame[0],good_data_frame[1])
                    df['traveltime'] = df['traveltime'] * (distance / good_distance)
                    model,copy_df,features = model_stop(df)
                    with open('/data/linear_models3/'+str(stopA)+'_'+str(stopB) + '.bin','wb') as handle:
                        pickle.dump(model,handle,protocol = pickle.HIGHEST_PROTOCOL)
                    
            
    return True        
def validate_model(model,df,features):
    preds = model.predict(df[features])
    #print(preds.min())
    #print(preds.max())
    #print(preds.mean())
    #print(metrics.r2_score(df['traveltime'],preds))
    #print(preds.max() > df['traveltime'].quantile(q=0.001))
    
    if preds.min() < -1:
        return False
    elif metrics.r2_score(df['traveltime'],preds) < 0:
        return False
    elif preds.mean() > 1000:
        return False
    elif preds.max() > preds.mean() * 4 :
        return False    
    else:
        return True

def write_error(error):
    f = open('/data/linear_models3/errorlog.log','a')
    f.write(error)
    f.close()
    

def model_exists(stopA,stopB):
    model_dir = '/data/linear_models3'
    if os.path.exists(model_dir+'/'+str(stopA)+'_'+str(stopB)+'.bin'):
        return True
    else:
        return False

def stop_link_has_data(stopA,stopB):
    df = stop_tools.stop_data(str(stopA),str(stopB))


model_dir = '/data/linear_models3/'
import pickle
import os
from dbanalysis import stop_tools
from subprocess import call
call(['mkdir','/data/linear_models3'])
call(['touch',model_dir+'errorlog.log'])
import json
from sklearn import metrics
from sklearn.linear_model import LinearRegression as lr
import copy
import pandas as pd
real_stops = {}
fake_models = {}
count = 0
routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
for route in routes:
    
    for v_num,variation in enumerate(routes[route]):
        count +=1 
        print(route,v_num)
        print(count,'/',468,'\n\n')
        a=model_route(route,variation,v_num)
        if a == False:
            write_error('too few stops for ' + str(route) + '_' + str(v_num) + '\n')
        try:
            pass
        except:
            write_error('failed for ' + str(route) + '_' + str(v_num) + '\n')      
      


