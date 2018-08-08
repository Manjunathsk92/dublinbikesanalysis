from simple_network import network
import pickle
import time
t1 = time.time()
with open('networkpickle.bin','rb') as handle:
    n = pickle.load(handle)


for node in n.nodes:

    if n.nodes[node].timetable.to_concat != []:
        n.nodes[node].timetable.concat_and_sort()


print(time.time() - t1)
