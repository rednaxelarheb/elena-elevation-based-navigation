from flask import Flask, request, jsonify, render_template, Response
import json
import sys
sys.path.insert(-1, '../')
import jsonschema

from path_finding import download_graph
from path_finding import solver
from path_finding import *

# load flask server config from json and update setting
settings_path = './appconfig.json'
json_data = open(settings_path).read()
settings = json.loads(json_data)

params = {}
app = Flask(__name__, **params)
app.config.update(settings)


# TODO: this route strangely does NOT match /index.html (which is the same route by internet conventions. fix this)
@app.route('/', methods=['GET'])
def index():
    # TODO implement default app route page to be returned
    return render_template('index.html')


"""
This is the main route to compute the route for the data the user passed in.
EXPECTED FORMAT OF JSON PASSED IN:
{
"start_address": {
"latitude": FLOAT,
"longitude": FLOAT
}, 
"max_or_minimize_change": Boolean,
length: FLOAT
}
"""
@app.route('/get_route', methods=['POST'])
def get_route():
    input_data = request.get_json()

    valid = validate_json_in(input_data)
    if valid:

        latitude = float(input_data['start_address']['latitude'])
        longitude = float(input_data['start_address']['longitude'])
        radius = input_data['length'] / 2
        unknown_parameter = 0.001 #input_data['max_or_minimize_change'] (the elevation change we are looking for)

        # TODO process input data and compute best route and return it for rendering

        graph = download_graph(latitude, longitude, radius)
        desired_profile = path_profile().from_total_uphill_and_dist(100, radius*2) #need to get elevation change (in place of 100) from front end
        res = solver(graph, latitude, longitude, desired_profile).solve()
        print(res)
        routes = {}
        count = 0;
        edge_sequence = graph.es
        for route in res:
            edges = route[0]
            index = 0
            path = []

            for edge in edges:
                if index == 0:
                    vertexid = edge_sequence[edge].source
                    #graph.vs[vertexid]
                    # elevation_change = graph.es[edge].attributes().get('grade') #elevation change
                    path.append({'total_elevation_change': route[1]})
                    path.append({'distance': route[2]})
                    point = {"latitude": graph.vs[vertexid].attributes().get('y'), "longitude": graph.vs[vertexid].attributes().get('x'), "gradient": graph.es[edge].attributes().get('grade')}
                    path.append(point)
                    vertexid2 = edge_sequence[edge].target
                    point = {"latitude": graph.vs[vertexid2].attributes().get('y'), "longitude": graph.vs[vertexid2].attributes().get('x'), "gradient": graph.es[edge].attributes().get('grade')}
                    path.append(point)
                    index+=2
                else:
                    vertexid = edge_sequence[edge].target
                    point = {"latitude": graph.vs[vertexid].attributes().get('y'), "longitude": graph.vs[vertexid].attributes().get('x'), "gradient": graph.es[edge].attributes().get('grade')}
                    path.append(point)
                    index +=1




            count+=1
            route_name = "route%d" % count
            # print(path)

            routes[route_name] = path #


        return jsonify(routes)
    else: #invlaid json was passed in
        return Response("{}", status=600, mimetype='application/json') #


#helper function that ensures the data passed into get_route follows our schema
def validate_json_in(input_data):
    with open('schemas/get_route_schema.json') as json_file:
        schema = json.load(json_file)
        try:
            jsonschema.validate(input_data, schema)
            return True
        except:
            return False


if __name__ == '__main__':
    app.run()
