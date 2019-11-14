from flask import Flask, request, jsonify, render_template
import json
import sys
# sys.path.insert(-1, '../')

from path_finding import download_graph
from path_finding import solver

# load flask server config from json and update setting
settings_path = './appconfig.json'
json_data = open(settings_path).read()
settings = json.loads(json_data)

params = {}
app = Flask(__name__, **params)
app.config.update(settings)


# TODO: this route strangely does NOT match /index.html (which is the same route by internet conventions. fix this)
@app.route('/', methods=['GET', 'POST'])
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
    input_data = json.loads(request.get_json())
    # TODO validate json passed in using jsonvalidator library?
    # print(input_data['start_address']['latitude'])
    latitude = float(input_data['start_address']['latitude'])
    longitude = float(input_data['start_address']['longitude'])
    radius = input_data['length'] / 2
    unknown_parameter = 0.001 #input_data['max_or_minimize_change'] (the elevation change we are looking for)

    # TODO process input data and compute best route and return it for rendering

    graph = download_graph.get_graph(latitude, longitude, radius)
    res = solver.solver(graph, latitude, longitude, unknown_parameter, radius*2).solve()

    routes = {}
    count = 0;
    edge_sequence = graph.es
    vertex_sequence = graph.vs
    for route in res:
        edges = route[0]
        index = 0
        path = []

        for edge in edges:
            if index == 0:
                vertexid = edge_sequence[edge].source
                #graph.vs[vertexid]
                # elevation_change = graph.es[edge].attributes().get('grade') #elevation change
                point = {"latitude": graph.vs[vertexid].attributes().get('y'), "longitude": graph.vs[vertexid].attributes().get('x'), "elevation_change": 0}
                path.append(point)
                vertexid2 = edge_sequence[edge].target
                point = {"latitude": graph.vs[vertexid2].attributes().get('y'), "longitude": graph.vs[vertexid2].attributes().get('x'), "elevation_change": graph.es[edge].attributes().get('grade')}
                path.append(point)
                index+=2
            else:
                vertexid = edge_sequence[edge].target
                point = {"latitude": graph.vs[vertexid].attributes().get('y'), "longitude": graph.vs[vertexid].attributes().get('x'), "elevation_change": 0}
                path.append(point)
                index +=1




        count+=1
        route_name = "route%d" % count
        # print(path)

        routes[route_name] = path
    #total change
    # altitude_change = route[1]
    # distance = route[2]

    # print("this function was called)")
    # print(routes)
    # print(res)
    return jsonify(routes)



if __name__ == '__main__':
    app.run()
