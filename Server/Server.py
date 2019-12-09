from flask import Flask, request, jsonify, render_template, Response
import json
import sys
sys.path.insert(-1, '../')
import jsonschema
import typing

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


def validate_json_in(input_data: typing.Dict[str, typing.Any]) -> bool:
    ''' Helper function that enforces that the data passed into get_route follows our schema '''
    try:
        jsonschema.validate(input_data, get_route_schema)
        return True
    except Exception as e:
        print(e)
        return False



def get_route_helper(latitude: float, longitude: float, desired_distances: typing.List[float], desired_altitudes: typing.List[float]):
    '''Interfaces with the solver (see path_finding.solver) to find routes.

    Args:
        latitude: the latitude of the starting location
        longitude: the longitude of the starting location
        desired_distances: the desired distances, in meters
        desired_altitudes: the desired altitudes, in meters

    Returns: A list of dictionaries with the following keys:
        * vertex_locations: a list of dicts with (longitude, latitude) keys. See path_finding.path_objects.path_object.get_vertex_locations.
        * textual_directions: a string, text directions for the path, in plain english.
        * total_uphill: the total uphill altitude travelled, in meters. See path_finding.path_objects.path_profile.total_uphill.
        * total_distance: the total distance travelled, in meters. See path_finding.path_objects.path_profile.total_distance.
        * slopes: a list with the slope of each edge in the path. See path_finding.path_objects.path_profile.get_slopes.
        * distances: a list of distances, in meters, representing the distances traversed at each vertex. See path_finding.path_objects.path_profile.distances.
        * altitudes: a list of altitudes, in meters, representing the altitude (relative to the starting point) of each vertex. See path_finding.path_objects.path_profile.altitudes.
    
    '''
    radius = 0.000621371 * desired_distances[-1] / 2 # converts meters to miles
    graph = download_graph(latitude, longitude, radius)
    desired_profile = path_profile().from_altitudes_distances(desired_altitudes, desired_distances)
    solutions = solver(graph, latitude, longitude, desired_profile).solve()
    routes = []
    for path_obj in solutions:
        profile = path_obj.get_profile()
        routes.append({
            'vertex_locations': path_obj.get_vertex_locations(),
            'textual_directions': path_obj.get_text_directions(),
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
    ''' See `get_route_schema.json` for this API method's expected input format. '''
    input_data = request.get_json()
    # validate input
    if not validate_json_in(input_data):
        return Response("{}", status=600, mimetype='application/json') # response was invalid

    # ingest input
    latitude = float(input_data['start_address']['latitude'])
    longitude = float(input_data['start_address']['longitude'])
    desired_distances = input_data['desired_profile']['distances']
    desired_altitudes = input_data['desired_profile']['altitudes']
    # we can remove total distance and uphill; these are implied by the profile
    #total_distance = float(input_data['length'])
    #total_uphill = float(input_data['desired_uphill'])
 
    # get routes
    routes = get_route_helper(latitude, longitude, desired_distances, desired_altitudes)
    return jsonify(routes)


if __name__ == '__main__':
    app.run()
