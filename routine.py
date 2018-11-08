import logging
import requests
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class LightScene(object):
    """
    A scene is the basic unit of a routine which controls the lights.
    """
    def __init__(self, hue_light_code, ifttt_key, play_time):
        """
        Create the scene
        :param hue_light_code: code in the ifttt url
        :param play_time: amount of time that this scene will play
        """
        self.hue_light_url = "https://maker.ifttt.com/trigger/{code}/with/key/{key}".format(code=hue_light_code,
                                                                                            key=ifttt_key)
        self.play_time = play_time

class MoodRoutine(object):
    """
    A routine is composed of a song and multiple scenes
    """
    def __init__(self, name, dl_track_id):
        """
        Create the routine
        :param dl_track_id: a google drive download url code
        """
        self.name = name
        self.dl_track_url = "https://drive.google.com/uc?export=download&id={}".format(dl_track_id)
        self.light_scenes = []
        self.current_scene_index = 0

    def add_light_scene(self, light_scene):
        self.light_scenes.append(light_scene)

    def play_next_scene(self):
        """
        Play next scene will automatically reset to the beginning if the index
        exceeds the scene array length
        :return:
        """
        if not self.current_scene_index < len(self.light_scenes):
            self.current_scene_index = 0
        scene = self.light_scenes[self.current_scene_index]
        logger.info("calling lights api: {}".format(scene.hue_light_url[30:50]))
        requests.post(scene.hue_light_url, data={})
        time.sleep(scene.play_time)
        self.current_scene_index += 1

def generate_routine_dict_from_config(config):
    """
    Takes a yaml config with the correct format and turns it into a
    dictionary of moods mapped to routines.
    :param config: yaml config
    :return:
    """
    ifttt_key = config['secrets']['ifttt_code']
    routine_mapper = {}
    sequences = config['mood_sequences']
    for sequence in sequences:
        mood = sequence['name']
        routine = MoodRoutine(mood,sequence['song_url'])
        for light_scene in sequence['light_sequence']:
            routine.add_light_scene(LightScene(light_scene['hue_url'], ifttt_key, light_scene['play_time']))
        routine_mapper[mood] = routine
    return routine_mapper
