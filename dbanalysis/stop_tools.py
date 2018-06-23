"""

Set of functions for retrieving and analyzing stop-stop links. 

"""


def get_stop_link(stopA,stopB):
    
    """
    Retrieve the data describing the link between two stops
    """
    import os
    import pandas as pd
    from dbanalysis import headers as hds
    if not os.path.exists('/home/student/data/stops/'+str(stopA) +'/' + str(stopB) +'.csv'):
        print('Error - stop link data not on disk')
    else:
        df=pd.read_csv('/home/student/data/stops/'+str(stopA) +'/' + str(stopB) +'.csv', names=hds.get_stop_link_headers())
        df['stopA'] = stopA
        df['stopB'] = stopB
        return df
 



