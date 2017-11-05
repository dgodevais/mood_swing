import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class MoodMapper:
    def __init__(self, config_json):
        self.config = config_json
        self.mood_mapper = {}
        self.mood_to_spotify_url_mapper = {}
        self.mood_to_hue_mapper = {}

    def add_synonyms_for_mood_to_mapper(self, mood):
        mood_formatted = mood.replace('\n', '').replace(' ', '')
        logger.info('Getting synonyms for mood: {}'.format(mood_formatted))
        url = 'http://words.bighugelabs.com/api/2/{key}/{word}/json'.format(key=self.config['thesaurus_api_key'],
                                                                            word=mood_formatted)
        try:
            resp = requests.get(url)
            data = json.loads(resp.text)
            for synonym in data['adjective']['syn']:
                if synonym not in self.mood_mapper:
                    self.mood_mapper[synonym] = mood
            for sim in data['adjective']['sim']:
                if sim not in self.mood_mapper:
                    self.mood_mapper[sim] = mood
        except requests.RequestException as e:
            logger.error('Request failed: ' + str(e))
        except ValueError as e:
            logger.error('Request failed: ' + str(e))
        except KeyError as e:
            logger.error('Request failed: ' + str(e))

    def get_all_moods(self):
        return self.mood_mapper.keys()


