# -*- coding: utf-8 -*-
from app import app
import camra
from wordFilter import * 
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

    def test_wordFilter_createBadWordsENG(self):
        result = createBadWordsENG()
        actual = ["anal", "anus", "ballsack", "blowjob", "boner",
           "cock", "cunt", "dick", "dildo", "dyke",
           "fag", "fuck", "jizz", "muff", "nigger",
           "nigga", "penis", "piss", "pussy",
           "scrotum", "sex", "shit", "slut",
           "smegma", "spunk", "twat", "vagina",
           "wank", "whore", "erection"]
        self.assertEqual(result, actual)
    
    def test_wordFilter_createBadWordsRUS(self):
        result = createBadWordsRUS()
        actual = ["выёбываться", "гандон", "говно", "говнюк",
           "голый", "дать пизды", "дерьмо", 
           "дрочить", "другой дразнится", "ёбарь",
           "ебать-копать", "ебло", "ебнуть",
           "ёб твою мать", "жопа", "жополиз", 
           "играть на кожаной флейте", "измудохать",
           "каждый дрочит как он хочет", "какая разница",
           "как два пальца обоссать", "курите мою трубку",
           "лысого в кулаке гонять", "малофя", "манда"]
        self.assertEqual(result, actual)

    def test_wordFilter_filterBadSongs_true(self):
        result = filterBadSongs("shit")
        self.assertEqual(result, True)

    def test_wordFilter_filterBadSongs_false(self):
        result = filterBadSongs("happy")
        self.assertEqual(result, False)

    def test_wordFilter_filterBadSongs_none(self):
        result = filterBadSongs(None)
        self.assertEqual(result, True)

    def test_wordFilter_censorFilteredWords_true(self):
        result = censorFilteredWords("shit")
        self.assertEqual(result, "****")

    def test_wordFilter_censorFilteredWords_false(self):
        result = censorFilteredWords("happy")
        self.assertEqual(result, "happy")

    def test_wordFilter_censorFilteredWords_none(self):
        result = censorFilteredWords(None)
        self.assertEqual(result, True)
    
    def test_filterUsername_None(self):
        result = camra.filterUsername(None, None)
        self.assertEqual(result, -1)

    def test_filterUsername_short(self):
        result = camra.filterUsername("abc", "123")
        self.assertEqual(result, -1)
    
    def test_filterUsername_long(self):
        result = camra.filterUsername("qwertyuiopasdfgjklmzvnkjsfjsfasfd", "qwertyuiopasdfgjklmzvnkjsfjsfasfd")
        self.assertEqual(result, -1)

    def test_filterUsername_specialchars(self):
        result = camra.filterUsername("~!@#$%^&*()", "~!@#$%^&*()")
        self.assertEqual(result, -1)
    
    def test_filterUsername_specialchars1(self):
        result = camra.filterUsername("#abcdefg", "$abcdefg")
        self.assertEqual(result, -1)

    def test_filterUsername_specialchars2(self):
        result = camra.filterUsername("a%bcdefg", "abc*defg")
        self.assertEqual(result, -1)

    def test_filterUsername_specialchars3(self):
        result = camra.filterUsername("abc&defg", "abc&defg")
        self.assertEqual(result, -1)

    def test_filterUsername_specialchars4(self):
        result = camra.filterUsername("abc*defg", "abc*defg")
        self.assertEqual(result, -1)

    def test_filterUsername_specialchars5(self):
        result = camra.filterUsername("abc(defg", "abc)defg")
        self.assertEqual(result, -1)

    def test_filterUsername_goodTest(self):
        result = camra.filterUsername("goodusername", "goodpassword")
        self.assertEqual(result, 1)

