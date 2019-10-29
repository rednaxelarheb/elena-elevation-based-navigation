from flask import Flask, request, jsonify, render_template
import os
import json


settings_path = 'appconfig.json'
json_data = open(settings_path).read()
settings = json.loads(json_data)

params = {}
app = Flask(__name__, **params)
params['static_url_path'] = settings['STATIC_URL_PATH']
app.config.update(settings)
print(app.static_url_path, 'static_folder:', app.static_folder, 'STATIC_FOLDER:', app.config['STATIC_URL_PATH'],
      'MYSQL_DATABASE_URL:', app.config['MYSQL_DATABASE_USER'])


@app.route('/', methods=['GET', 'POST'])
def index():
    # TODO implement default app route page to be returned

    return render_template('index.html')


if __name__ == '__main__':

    app.run()