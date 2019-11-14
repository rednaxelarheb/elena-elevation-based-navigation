import unittest
import requests
import json


def test_get_route():
    # payload = {
    #     "start_address": {
    #         "latitude": 42.391155,
    #         "longitude": -72.526711
    #     },
    #     "max_or_minimize_change": True,
    #     'length': 5
    # }
    payload = {
        "start_address": {
            "latitude": 50,
            "longitude": 50
        },
        "max_or_minimize_change": True,
        'length': 2
    }
    r = requests.post('http://localhost:5000/get_route', json=json.dumps(payload))
    print(r.status_code)
    print(r.json())


"""
[edge_numbers,...], altitude change, distance)
([280, 281], 0.0314, 146.526)
"""
if __name__ == '__main__':
    test_get_route()
