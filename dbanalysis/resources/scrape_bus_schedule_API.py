import requests
import json
import os

def getDepartTime(filename):
    """Function that takes the the trimmed_routes.json as argument and returns scheduled departure times for the first terminus of each route in json format"""

    f = '/home/student/dbanalysis/dbanalysis/resources/'+filename
    if os.path.exists(f) is True:
        with open(f) as fin:  # this is new
            data = json.loads(fin.read())
            
            #Extracting keys of json file which are all the bus routes
            routes= data.keys()
            route_list =list(routes)

            #Making a dict that lists all a route's stops 
            route_dict  = {}
            for key in route_list:
                og_stops = []
                for i,stops in enumerate(data[key]): 
                    og_stop = stops[1]
                    og_stops.append(og_stop)
                route_dict[key] = og_stops

            #Scraping data into a new dict subbing key and values from route_dict as parameters 
            routes_schedule={}
            for key, value in route_dict.items():
                for og_stop in value:
                    parameters = {"stopid": og_stop, "routeid": key}
                    response3 = requests.get("https://data.smartdublin.ie/cgi-bin/rtpi/timetableinformation?type=week&format=json", params=parameters)
                    
                    bus_data={}
                    if response3.status_code == 200:
                        bus_timetable = response3.json()
                        try:
                            if bus_timetable['errorcode']=="0":
                                bus_data['route']=bus_timetable['route']
                                bus_data['stopid']=bus_timetable['stopid']
                                bus_data['destination']=bus_timetable['results'][0]['destination']
                                bus_data['startdayofweek']=bus_timetable['results'][0]['startdayofweek']
                                bus_data['enddayofweek']=bus_timetable['results'][0]['enddayofweek']
                                bus_data['first_departure']=bus_timetable['results'][0]['departures'][0]
                                bus_data['last_departure']=bus_timetable['results'][0]['departures'][-1]

                                bus_data['destination1']=bus_timetable['results'][1]['destination']
                                bus_data['startdayofweek1']=bus_timetable['results'][1]['startdayofweek']
                                bus_data['enddayofweek1']=bus_timetable['results'][1]['enddayofweek']
                                bus_data['first_departure1']=bus_timetable['results'][1]['departures'][0]
                                bus_data['last_departure1']=bus_timetable['results'][1]['departures'][-1]

                                bus_data['destination2']=bus_timetable['results'][2]['destination']
                                bus_data['startdayofweek2']=bus_timetable['results'][2]['startdayofweek']
                                bus_data['enddayofweek2']=bus_timetable['results'][2]['enddayofweek']
                                bus_data['first_departures2']=bus_timetable['results'][2]['departures'][0]
                                bus_data['last_departures2']=bus_timetable['results'][2]['departures'][-1]


                                bus_data['destination3']=bus_timetable['results'][3]['destination']
                                bus_data['startdayofweek2']=bus_timetable['results'][3]['startdayofweek']
                                bus_data['enddayofweek2']=bus_timetable['results'][3]['enddayofweek']
                                bus_data['first_departures2']=bus_timetable['results'][3]['departures'][0]
                                bus_data['last_departures2']=bus_timetable['results'][3]['departures'][-1]


                                bus_data['destination4']=bus_timetable['results'][4]['destination']
                                bus_data['startdayofweek2']=bus_timetable['results'][4]['startdayofweek']
                                bus_data['enddayofweek2']=bus_timetable['results'][4]['enddayofweek']
                                bus_data['first_departures2']=bus_timetable['results'][4]['departures'][0]
                                bus_data['last_departures2']=bus_timetable['results'][4]['departures'][-1]


                                bus_data['destination5']=bus_timetable['results'][5]['destination']
                                bus_data['startdayofweek2']=bus_timetable['results'][5]['startdayofweek']
                                bus_data['enddayofweek2']=bus_timetable['results'][5]['enddayofweek']
                                bus_data['first_departures2']=bus_timetable['results'][5]['departures'][0]
                                bus_data['last_departures2']=bus_timetable['results'][5]['departures'][-1]


                                bus_data['destination6']=bus_timetable['results'][6]['destination']
                                bus_data['startdayofweek6']=bus_timetable['results'][6]['startdayofweek']
                                bus_data['enddayofweek6']=bus_timetable['results'][6]['enddayofweek']
                                bus_data['first_departures6']=bus_timetable['results'][6]['departures'][0]
                                bus_data['last_departures6']=bus_timetable['results'][6]['departures'][-1]


                                bus_data['destination7']=bus_timetable['results'][7]['destination']
                                bus_data['startdayofweek7']=bus_timetable['results'][7]['startdayofweek']
                                bus_data['enddayofweek7']=bus_timetable['results'][7]['enddayofweek']
                                bus_data['first_departures7']=bus_timetable['results'][7]['departures'][0]
                                bus_data['last_departures7']=bus_timetable['results'][7]['departures'][-1]


                                bus_data['destination8']=bus_timetable['results'][8]['destination']
                                bus_data['startdayofweek8']=bus_timetable['results'][8]['startdayofweek']
                                bus_data['enddayofweek8']=bus_timetable['results'][8]['enddayofweek']
                                bus_data['first_departures8']=bus_timetable['results'][8]['departures'][0]
                                bus_data['last_departures8']=bus_timetable['results'][8]['departures'][-1]
                    


                                
                                
                        except IndexError:
                                print("This row doesn't have all indexes requested, but here is the row...")
                                print(bus_timetable['results'])

                        else:
                            #append bus_data dict into second dictionary 
                            routes_schedule[key]={'bus_data':bus_data}
                            print('Stop {}, Route {}, Errorcode {}'.format(value,key,bus_timetable['errorcode']))
                                
                                
    with open('Bus_stops_schedule.json','w') as f:
        json.dump(routes_schedule, f, indent=4)         