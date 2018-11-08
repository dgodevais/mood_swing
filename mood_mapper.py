import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MoodMapper:
    def __init__(self, config_json):
        self.config = config_json
        self.mood_mapper = {}
        self.mood_to_music_url_mapper = {}
        self.mood_to_hue_mapper = {}

        with open('moods_master.txt', 'r') as f:
            logger.info('Mapping moods to correct music and hue urls.')
            moods = f.readlines()
            for mood in moods:
                mood_formatted = mood.replace('\n', '').replace(' ', '')
                self.mood_mapper[mood_formatted] = mood_formatted
                mood_music_key = '{}_url'.format(mood_formatted)
                self.mood_to_music_url_mapper[mood_formatted] = self.config['music'][mood_music_key]
                mood_hue_key = '{}_url'.format(mood_formatted)
                self.mood_to_hue_mapper[mood_formatted] = self.config['ifttt'][mood_hue_key]

    def add_synonyms_for_mood_to_mapper(self, mood):
        mood_formatted = mood.replace('\n', '').replace(' ', '')
        logger.info('Getting synonyms for mood: {}'.format(mood_formatted))
        key = self.config['secrets']['thesaurus_api_key']
        url = 'http://words.bighugelabs.com/api/2/{key}/{word}/json'.format(key=key, word=mood_formatted)
        try:
            resp = requests.get(url)
            data = json.loads(resp.text)
            for synonym in data['adjective']['syn']:
                if synonym not in self.mood_mapper:
                    self.mood_mapper[synonym] = mood_formatted
                    mood_music_key = '{}_url'.format(mood_formatted)
                    self.mood_to_music_url_mapper[synonym] = self.config['music'][mood_music_key]
                    mood_hue_key = '{}_url'.format(mood_formatted)
                    self.mood_to_hue_mapper[synonym] = self.config['ifttt'][mood_hue_key]
            for sim in data['adjective']['sim']:
                if sim not in self.mood_mapper:
                    self.mood_mapper[sim] = mood_formatted
                    mood_music_key = '{}_url'.format(mood_formatted)
                    self.mood_to_music_url_mapper[sim] = self.config['music'][mood_music_key]
                    mood_hue_key = '{}_url'.format(mood_formatted)
                    self.mood_to_hue_mapper[sim] = self.config['ifttt'][mood_hue_key]
            logger.info('Finished retrieving mood synonyms.')
        except requests.RequestException as e:
            logger.error('Request failed: ' + str(e))
        except ValueError as e:
            logger.error('Request failed: ' + str(e))
        except KeyError as e:
            logger.error('Request failed: ' + str(e))

    def get_all_moods(self):
        return self.mood_mapper.keys()
