import linear_network
import time
g=linear_network.bus_network()
for n in g.nodes:
    g.nodes[n].get_foot_links()


visited = []
unvisited = []
current_time = 30000
stop = '246'
links = set([[i for i in g.nodes['246'].get_links() if i in g.nodes] + [i for i in g.nodes['246'].foot_links if i in g.nodes]])
print(links)

    





