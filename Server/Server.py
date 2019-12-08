from flask import Flask, request, jsonify, render_template, Response
import json
import sys
sys.path.insert(-1, '../')
import jsonschema

from path_finding import download_graph, solver, path_object, path_profile


# load flask server config from json and update setting
settings_path = '../Server/appconfig.json'
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
        total_uphill_desired = 100 #TODO get from front end


        graph = download_graph(latitude, longitude, radius)
        desired_profile = path_profile().from_total_uphill_and_dist(total_uphill_desired, radius*2) #need to get elevation change (in place of 100) from front end
        res = solver(graph, latitude, longitude, desired_profile).solve()
        routes = {}
        count = 0
        for route in res:
            ######
            path = []
            locations = route.get_vertex_locations()
            slopes = route.get_profile().get_slopes()
            distances = route.get_profile().distances



            ind = 0
            cur_total = 0
            for x in locations:
                if ind < len(distances) -1:
                    x['gradient'] = slopes[ind]
                    x['distance_to_next'] = distances[ind]
                    cur_total +=slopes[ind]*distances[ind]
                    ind +=1
                else:
                    print(x)
                    inverse = -1*cur_total/distances[ind] #aproximantion of what that last slope needs to be
                    x['gradient'] = inverse
                    x['distance_to_next'] = distances[ind]
                    ind += 1


            path.append({'total_elevation_change': route.get_profile().total_uphill})
            path.append({'distance': route.get_profile().total_distance})
            path.append(locations)
            path.append({"text_directions": route.get_text_directions()})

            count+=1
            route_name = "route%d" % count
            print(path) #DEBUG

            routes[route_name] = path
            if count>10:
                break

        return jsonify(routes)
    else: #invlaid json was passed in
        return Response("{}", status=600, mimetype='application/json') #


def validate_json_in(input_data) -> bool:
    ''' Helper function that enforces that the data passed into get_route follows our schema '''
    with open('schemas/get_route_schema.json') as json_file:
        schema = json.load(json_file)
        try:
            jsonschema.validate(input_data, schema)
            return True
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    app.run()
