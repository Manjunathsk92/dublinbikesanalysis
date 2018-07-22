#A set of tools for analyzing dublin bus data
Includes:
* route_tools -> functions for splitting dublin bus data
* scripts -> more functions for splitting bus data, and processing gtfs data
* resources -> Plenty of pickles and dictionaries, derived from gtfs data
* stop_tools -> the stop_getter (distance and shape retrieval) and stop_finder (find closest stops to given coordinates) classes, as well as some functions for retrieving and preprocessing data
* classes -> contains the stop_link model (a two fold model of a stop link) and the stop class (a container for stop links). Also contains the time_tabler classes (generate bus departure times,and store and retrieve timetables in an accessible format).
* network -> contains the network class that acts as a container for stops, as well as running routefinding algorithms and retrieving information about the dublin bus network.
