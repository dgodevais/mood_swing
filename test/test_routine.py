import unittest
import yaml

from routine import generate_routine_dict_from_config


class TestRoutines(unittest.TestCase):
    def setUp(self):
        with open('test_config.yaml', 'r') as f:
            self.test_config = yaml.load(f)

    def test_generate_routine_dict_from_config(self):
        mood_mapper = generate_routine_dict_from_config(self.test_config)
        self.assertEquals(mood_mapper['happy'].name, 'happy')
        self.assertEquals(mood_mapper['happy'].dl_track_url, 'https://drive.google.com/uc?export=download&id=asdf')
        self.assertEquals(len(mood_mapper['happy'].light_scenes), 1)

