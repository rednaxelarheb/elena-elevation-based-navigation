from flask import Flask, request, jsonify, render_template
import json

from path_finding import download_graph
from path_finding import solver

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
    #TODO validate json passed in using jsonvalidator library?
    print(input_data['start_address']['latitude'])
    latitude = input_data['start_address']['latitude']
    longitude = input_data['start_address']['longitude']
    radius = input_data['length']/2
    unknown_parameter = input_data['max_or_minimize_change']

    #TODO process input data and compute best route and return it for rendering

    graph = download_graph.get_graph(latitude, longitude, radius)
    res = solver(graph, latitude,longitude,unknown_parameter,input_data['length']).solve()

    print("this function was called)")
    return jsonify(res)




if __name__ == '__main__':
    app.run()