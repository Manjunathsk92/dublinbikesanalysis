"""

Big question here is - how to combine data that comes from separate routes?

Also, can we include the rows that get dropped by route_tools.get_munged_route_data?

Maybe we can just not bother about this in the network prototype/solve it later, when the data has been sqlized? Depending on query times, it should be pretty simple as long as the data has been sqlized properly.

"""
from dbanalysis.models import simple_link_model as slm
from dbanalysis.models import gather_link_data as gld
import pickle

class bus_network():

    def __init__(self,pickle_file=None):
            
            if pickle = None:
                self.make_sparse_adjacency_matrix()
                self.calculate_edge_distances()
                self.build_models()
                self.get_stop_coordinates()
            else:
                import pickle
                with open(pickle_file,'rb') as handle:
                    try:
                        self = pickle.load(handle)
                    except:
                        raise error
                        print('Pickle file is invalid')
            
        pass

    def make_sparse_adjacency_matrix(self):
        with open('/home/dbanalysis/dbanalysis/resources/stop_links.pickle') as handle:
        stop_links = pickle.load(handle)
        ajd_matrix = {}
        for stopa in stop_links:

            ajd_matrix[stopa] = {}
            for stopb in stop_links[stopa]:
                
                ajd_matrix[stopa][stopb]={}
        
        self.ajd_matrix = ajd_matrix            

    
