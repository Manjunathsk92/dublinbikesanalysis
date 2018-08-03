import sys
route = sys.argv[1]
variation = int(sys.argv[2])
from dbanalysis.models import BRM
from subprocess import call
import pickle
call(['mkdir','/data/BRM/'+route+'_'+str(variation)])
directory = '/data/BRM/'+route+'_'+str(variation) + '/'

model = BRM.BRModel(route,variation,rgr='Neural',mode='build')
with open(directory+'model.bin', 'wb') as handle:
    pickle.dump(model,handle,protocol=pickle.HIGHEST_PROTOCOL)
try:
    pass
except:

    f = open(directory + 'log.log','w')
    f.write('Error')
    f.close()
