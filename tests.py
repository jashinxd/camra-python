from app import app
import camra
import unittest

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_request_getLocation(self):
        result = camra.getLocation()
        self.assertEqual(result, "Cleveland")

    def test_request_getWeather(self):
        result = camra.getWeather()
        possibleWeathers = ["Thunderstorm", "Drizzle", "Rain", "Snow", "Clear", "Clouds", "Extreme"]
        self.assertIn(result, possibleWeathers)

    #def test_getLocationSongs(self):
    #    result = getLocationSongs()
    #    self.assertIsInstance(result, basestring)
        
        
if __name__ == '__main__':
        unittest.main()
