class selector():

    def __init__(self):
        import json
        from dbanalysis.stop_tools import stop_getter
        self.routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
        self.stops_dict = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','r').read())
        


    def return_all_routes(self):
        return {'routes':[route for route in self.routes]}

    def return_variations(self,route):
        return {route : ['Towards ' + variation[0] for variation in self.routes[route]]}

    def stops_in_route(self,route,variation):

        return [{'name': self.stops_dict[str(stop)]['stop_name'], 'id':str(stop)} \
                for stop in self.routes[route][variation][1:]]
    
    
if __name__ == '__main__':
    selector = selector()
    print(selector.return_all_routes())
    print(selector.return_variations('15'))
    print(selector.stops_in_route('15',0))
    
