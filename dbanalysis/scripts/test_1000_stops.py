MAPE = []
r2_scores = []
MAE = []
min_pred = 1000
from sklearn import metrics
from sklearn.neural_network import MLPRegressor
import pandas as pd
from dbanalysis import stop_tools

for i in range(1000):
    import pandas as pd

    df = stop_tools.random_stop_data()
    if df is None or df.shape[0] <= 100:
        continue
    df = pd.get_dummies(df,columns=['day','routeid','hour'])
    df['traveltime']=df['actualtime_arr_to'] - df['actualtime_arr_from']
    df = df[df['traveltime']>df['traveltime'].quantile(q=0.05)]
    features = ['rain','temp','vappr']
    for i in df.columns:
        if (i!='dayofservice' and i[0:3]=='day') or i[0:4] == 'hour' or i[0:5] == 'route':
            features.append(i)
    rgr = MLPRegressor(hidden_layer_sizes = (20,20,20,20)).fit(df[features],df['traveltime'])
    preds = rgr.predict(df[features])
    ma =((abs(df['traveltime']-preds)/df['traveltime'])*100).mean()
    mae = metrics.mean_absolute_error(df['traveltime'],preds)
    r2 = metrics.r2_score(df['traveltime'],preds)
    print(ma,mae,r2,preds.min())
    MAPE.append(ma)
    MAE.append(mae)
    if preds.min() < min_pred:
        min_pred = preds.min()
    r2_scores.append(r2)
    
print('\n\n\Average mape',MAPE/len(MAPE))
print('Average MAE',MAE/len(MAE))
print('Average r2 score',r2_scores/len(r2_scores))
print('Minimum prediction', min_pred)
