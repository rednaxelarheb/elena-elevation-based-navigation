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
"""
@app.route('/get_route', methods=['POST'])
def get_route():
    input_data = request.get_json()
    #TODO process input data and compute best route and return it for rendering
    return jsonify("")




if __name__ == '__main__':
    app.run()