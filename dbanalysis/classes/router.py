class router():


    def __init__ (self,route,variation, array):

       self.descript = array[0]
       self.pattern = array[1:]
       self.route = route
       self.variation = variation
      

    def has_model(self):
        import os
        if os.path.exists('/data/BRM/'+self.route+'_'+str(self.variation)+'/model.bin'):
            return True
        else:
            return False

    def predict(self,df):
        from dbanalysis.models import BRM
        import pickle
        import pandas as pd
        with open('/data/BRM/'+self.route+'_'+str(self.variation)+'/model.bin','rb') as handle:
            model = pickle.load(handle)
        features = model.features
        X = pd.get_dummies(df,columns = ['day','month','hour'])
        for f in features:
            if f not in X.columns:
                X[f] = 0
        X['vappr'] = 10.00
        X = model.X_transformer.transform(X[features])
        preds = model.predict(X)
        real_preds = model.Y_transformer.inverse_transform(preds.reshape(-1,1))
        import numpy as np
        real_preds = np.array([i[0] for i in real_preds])
        del(model)
       
        df['actualtime_arr_to'] = df['actualtime_arr_from'] + real_preds
        return df

    def splice(self,df,arr):
        d = {}
        first = True
        for stopA in arr[:-1]:
            d[str(stopA)] = df[df['stopA'] == str(stopA)]
            if first:
                d[str(stopA)]['actualtime_arr_from'] = 0
                first = False
            else:
                d[str(stopA)]['actualtime_arr_from'] = arrs
            arrs = d[str(stopA)]['actualtime_arr_to']
            
        return d

    def generate_all_times(self,df):
        df = self.predict(df)
        d = self.splice(df,self.pattern)
        del(df)
        return d
if __name__ == '__main__':
    import time
    t1=time.time()
    from dbanalysis.classes import time_tabler_refac as time_tabler
    import datetime
    dt = datetime.datetime.now()
    t = time_tabler.time_tabler()
    df = t.get_dep_times_five_days('1',dt)
    df = t.add_distances(df)
    df = df[0]['matrix']
    
     
    import json
    routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
    arr = routes['1'][0]
    r = router('1',0,arr)
    df=r.predict(df)
    d=r.splice(df,arr[1:])
    
    print(time.time()-t1)
