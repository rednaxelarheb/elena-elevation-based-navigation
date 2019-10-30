from flask import Flask, request, jsonify, render_template
import json


settings_path = 'appconfig.json'
json_data = open(settings_path).read()
settings = json.loads(json_data)

params = {}
app = Flask(__name__, **params)
app.config.update(settings)



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
"other_points_to_include" = [
{
"latitude": FLOAT,
"longitude": FLOAT
},...
{
"latitude": FLOAT,
"longitude": FLOAT
}],

"max_or_minimize_change": Boolean,
"cycle_or_not": Boolean,

"end_address": {
"latitude": FLOAT,
"longitude": FLOAT
}}
"""
@app.route('/get_route', methods=['POST'])
def get_route():
    input_data = request.get_json()
    #TODO process input data and compute best route and return it for rendering
    return jsonify("")




if __name__ == '__main__':
    app.run()