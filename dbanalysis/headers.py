def get_route_headers():
	return ['index','datasource','dayofservice','tripid','progrnumber','stoppointid','plannedtime_arr','plannedtime_dep','actualtime_arr','actualtime_dep','vehicleid','passengers','passengersin','passengersout','distance','suppressed','justificationid','lastupdate','note']


def get_stop_link_headers():
    return ['index','dayofservice', 'tripid','plannedtime_arr_from','plannedtime_dep_from', 'actualtime_arr_from', 'actualtime_dep_from','plannedtime_arr_to', 'actualtime_arr_to', 'routeid']
