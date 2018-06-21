"""

Big question here is - how to combine data that comes from separate routes?

Also, can we include the rows that get dropped by route_tools.get_munged_route_data?

Maybe we can just not bother about this in the network prototype/solve it later, when the data has been sqlized? Depending on query times, it should be pretty simple as long as the data has been sqlized properly.

"""

class bus_network():

    def __init__(self,directory,mix_route_data=False,drop_rows=True):

        pass
