import pandas as pd
leavetimes = pd.read_csv('/home/student/data/rt_leavetimes_2017_I_DB.txt',delimiter=';',chunksize=1000000)
count=0
while True:
    print('reading chunk', count)
    count+=1
    chunk = leavetimes.get_chunk(1000000)
    stops=chunk['stoppointid'].unique()
    if '2681' in [str(stop) for stop in stops] or 2681 in [int(stop) for stop in stops]:
        print('found')
        break
    del(stops)
    del(chunk)
