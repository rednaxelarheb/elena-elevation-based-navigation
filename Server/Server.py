from flask import Flask, request, jsonify, render_template, Response
import json
import sys
sys.path.insert(-1, '../')
import jsonschema

from path_finding import download_graph, solver, path_object, path_profile


# load flask server config from json and update setting
settings_path = '../Server/appconfig.json'
get_route_schema_path = '../Server/schemas/get_route_schema.json'

with open(settings_path) as f:
    settings = json.load(f)

with open(get_route_schema_path) as f:
    get_route_schema = json.load(f)

params = {}
app = Flask(__name__, **params)
app.config.update(settings)


def validate_json_in(input_data) -> bool:
    ''' Helper function that enforces that the data passed into get_route follows our schema '''
    try:
        jsonschema.validate(input_data, get_route_schema)
        return True
    except Exception as e:
        print(e)
        return False



def get_route_helper(latitude: float, longitude: float, total_distance: float, total_uphill: float):
    '''Interfaces with the solver (see path_finding.solver) to find routes.

    Args:
        latitude: the latitude of the starting location
        longitude: the longitude of the starting location
        total_distance: the desired total distance, in meters
        total_uphill: the desired total uphill altitude, in meters

    Returns: A list of dictionaries with the following keys:
        * vertex_locations: a list of dicts with (longitude, latitude) keys. See path_finding.path_objects.path_object.get_vertex_locations.
        * total_uphill: the total uphill altitude travelled, in meters. See path_finding.path_objects.path_profile.total_uphill.
        * total_distance: the total distance travelled, in meters. See path_finding.path_objects.path_profile.total_distance.
        * slopes: a list with the slope of each edge in the path. See path_finding.path_objects.path_profile.get_slopes.
        * distances: a list of distances, in meters, representing the distances traversed at each vertex. See path_finding.path_objects.path_profile.distances.
        * altitudes: a list of altitudes, in meters, representing the altitude (relative to the starting point) of each vertex. See path_finding.path_objects.path_profile.altitudes.
    
    '''
    radius = 0.000621371 * total_distance / 2 # converts meters to miles
    graph = download_graph(latitude, longitude, radius)
    desired_profile = path_profile().from_total_uphill_and_dist(total_uphill, total_distance)
    cost_fn = None # TODO use a different cost function
    solutions = solver(graph, latitude, longitude, desired_profile, cost_fn).solve()
    routes = []
    for path_obj in solutions:
        profile = path_obj.get_profile()
        routes.append({
            'vertex_locations': path_obj.get_vertex_locations(),
            'total_uphill': profile.total_uphill,
            'total_distance': profile.total_distance,
            'slopes': profile.get_slopes(),
            'distances': profile.distances,
            'altitudes': profile.altitudes
        })
    return routes


#match either route
@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    return render_template('index.html')




@app.route('/get_route', methods=['POST'])
def get_route():
    '''
    EXPECTED FORMAT OF JSON PASSED IN:
    {
        "start_address": {
            "latitude": FLOAT,
            "longitude": FLOAT
        }, 
        "desired_uphill": FLOAT,
        "length": FLOAT
    }
    '''
    input_data = request.get_json()
    # validate input
    if not validate_json_in(input_data):
        return Response("{}", status=600, mimetype='application/json') # response was invalid

    # ingest input
    latitude = float(input_data['start_address']['latitude'])
    longitude = float(input_data['start_address']['longitude'])
    total_distance = input_data['length']
    total_uphill = 0  # Default to we want a flat route
    if 'desired_uphill'  in input_data:  # Set how parameter for amount of uphill desired in users route
        total_uphill = float(input_data['desired_uphill'])

    # get routes
    routes = get_route_helper(latitude, longitude, total_distance, total_uphill)
    return jsonify(routes)


if __name__ == '__main__':
    app.run()
