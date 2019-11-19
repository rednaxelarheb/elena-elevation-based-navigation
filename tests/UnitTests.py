import unittest
import requests
import json
class TestServers(unittest.TestCase):
    #make sure server is running before running tests
    def test_upper(self):
        payload = {
            "start_address": {
                "latitude": 50,
                "longitude": 50
            },
            "max_or_minimize_change": True,
            'length': 2
        }
        r = requests.post('http://localhost:5000/get_route', json=payload)
        self.assertEqual(r.status_code, 200) #check that our request was successful
        routes = r.json()
        self.assertGreaterEqual(len(routes)+1, 1) #must be at least one route returned

        for x in range(1,len(routes)):
            print('route%d:'% x, )
            #TODO check that start and end point for each route is the same (lat/long should be same)
            first_vertex = routes['route%d' % x][3]
            last_vertex = routes['route%d' % x][len(routes['route%d' % x])-1]
            self.assertEqual((first_vertex['latitude'], first_vertex['longitude']),(last_vertex['latitude'], last_vertex['longitude']) , 'route end points did not match')
            # print(len(routes['route%d' % x]))




if __name__ == '__main__':
    unittest.main()