class selector():

    def __init__(self):
        import json
        from dbanalysis.stop_tools import stop_getter
        self.routes = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/trimmed_routes.json','r').read())
        self.stops_dict = json.loads(open('/home/student/dbanalysis/dbanalysis/resources/stops_trimmed.json','r').read())
        self.unavailable_routes = []
        f = open('/data/linear_models3/errorlog.log','r')
        text = f.read()
        arr = text.split('\n')[:-1]
        for line in arr:
            l = line.split(' ')
            p = l[4].split('_')
            self.unavailable_routes.append([p[0],int(p[1])])
            
        f.close()

    def return_all_routes(self):
        return {'routes':[route for route in self.routes]}

    def return_variations(self,route):
        return {route : ['Towards ' + variation[0] for variation in self.routes[route]]}

    def stops_in_route(self,route,variation):

        return [{'name': self.stops_dict[str(stop)]['stop_name'], 'id':str(stop)} \
                for stop in self.routes[route][variation][1:]]
    def get_unavailable(self,route,variation):
        if [route,variation] in self.unavailable_routes:
            return True
        else:
            return False
    
if __name__ == '__main__':
    selector = selector()
    print(selector.return_all_routes())
    print(selector.return_variations('15'))
    print(selector.stops_in_route('15',0))
    
