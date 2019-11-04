
import unittest
import requests
import json

def test_get_route():
    payload ={
        "start_address": {
            "latitude": 42.391155,
            "longitude": -72.526711
        },
        "max_or_minimize_change": True,
        'length': 5
    }
    r = requests.post('http://localhost:5000/get_route',json=json.dumps(payload))
    print(r.status_code)



if __name__ == '__main__':
    test_get_route()