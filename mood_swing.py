#!/usr/bin/python

import logging
import time
import yaml
from random import randint

import requests
from flask import Flask
from flask_ask import Ask, question, audio
from mood_mapper import MoodMapper
from pymongo import MongoClient
from routine import generate_routine_dict_from_config
from zappa.async import task

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

ask = Ask(app, "/")

DICT_OFFSET = 1
MOOD_ID = 'aaaaaaaaaaaaaaaaaaaaaaaa'
INITIAL_LIGHTS_TIMING_OFFSET = 2
PLAY_MOOD_TIMEOUT = 150

config = {}
with open('config.yaml', 'r') as f:
    config = yaml.load(f)
mood_mapper = generate_routine_dict_from_config(config)


mood_mapper = MoodMapper(config)
starter_moods = mood_mapper.get_all_moods()
for starter_mood in starter_moods:
    mood_mapper.add_synonyms_for_mood_to_mapper(starter_mood)

mood_to_music_url_map = mood_mapper.mood_to_music_url_mapper
mood_to_hue_map = mood_mapper.mood_to_hue_mapper

connection = MongoClient(config['secrets']['db_host'], config['secrets']['db_port'])
db = connection[config['secrets']['db_name']]
db.authenticate(config['secrets']['db_user'], config['secrets']['db_pass'])


mood_index = db['mood_index']
result = mood_index.update_one({'_id': MOOD_ID}, {"$set": {'active_mood':'default'}}, upsert=True)
logger.info('{} records modified.'.format(str(result.modified_count)))


@ask.launch
def start_skill():
    logger.info('Starting the Mood Swing Alexa skill.')
    my_name = config['secrets']['my_name']
    start_messages = {
        '0': my_name + ', what mood are you in?',
        '1': my_name + ', how are we feeling?',
        '2': 'What are your feels?',
        '3': 'Hi ' + my_name + ', tell me your mood.'
    }

    start_message = randint(0, len(start_messages) - DICT_OFFSET)
    welcome_message = start_messages[str(start_message)]
    return question(welcome_message)


@ask.intent("NevermindIntent")
def give_up():
    logger.info('Closing mood swing.')
    speech = "Fine then."
    return audio(speech)


@app.route('/')
def index():
    return 'Index Page', 200


@app.route('/set_mood_active_false')
def set_mood_active_false():
    logger.info('Setting mood active status to false')
    res = mood_index.update_one({'_id': MOOD_ID}, {"$set": {'active_mood': 'false'}}, upsert=True)
    if res.modified_count == 1:
        return 'active mood off', 200
    else:
        return 'active mood still off', 200


@app.route('/set_mood_active_true')
def set_mood_active_true():
    logger.info('Setting mood active status to true')
    res = mood_index.update_one({'_id': MOOD_ID}, {"$set": {'active_mood': 'true'}}, upsert=True)
    if res.modified_count == 1:
        return 'active mood on', 200
    else:
        return 'active mood still on', 200


@app.route('/mood_active_status')
def get_mood_active_status():
    res = mood_index.find_one({'_id': MOOD_ID})
    logger.info('Returning mood active status of {}'.format(res['active_mood']))
    return res['active_mood'], 200


@task
def play_mood_lights(hue_url, pause_time=17):
    is_active = 'true'
    loop_count = 0
    elapsed_time = pause_time * loop_count
    time.sleep(INITIAL_LIGHTS_TIMING_OFFSET)
    while is_active == 'true' and elapsed_time < PLAY_MOOD_TIMEOUT:
        logger.info("calling lights api: {} in loop {}".format(hue_url[30:50], str(loop_count)))
        requests.post(hue_url, data={})
        time.sleep(pause_time)
        is_active = requests.get(config['secrets']['status_url']).content
        loop_count += 1
        elapsed_time = pause_time * loop_count
    logger.info("Played mood {} for {} seconds".format(hue_url[30:50], str(elapsed_time)))


@ask.intent("MoodIntent")
def set_the_mood(my_mood):
    speech = "Setting the mood to {}".format(my_mood)
    logger.info(speech)
    if my_mood in mood_to_hue_map and my_mood in mood_to_music_url_map:
        stream_url = mood_to_music_url_map[my_mood]
        hue_url = mood_to_hue_map[my_mood]
        r = requests.get(config['secrets']['set_true_url'])
        if r.status_code == 200:
            play_mood_lights(hue_url, pause_time=17)
        else:
            logger.error(r.content)
        return audio(speech).play(stream_url)
    else:
        logger.info('{} not found in mood mapper'.format(my_mood))
        return stop()

# @ask.intent("ChangeIntent")
# def change_mood():
#     logger.info('Changing the mood.')
#     speech = "What would you like to change your mood to?"
#     normalize_lights()
#     return audio(speech)


def normalize_lights():
    logger.info('Resetting lights.')
    requests.get(config['secrets']['set_false_url'])
    requests.post(config['ifttt']['off_url'], data={})
    time.sleep(0.5)
    requests.post(config['ifttt']['normal_url'], data={})
    time.sleep(0.5)
    requests.post(config['ifttt']['normal_url'], data={})  # Ensure lights stay on


@ask.intent('AMAZON.PauseIntent')
def pause():
    logger.info('Pausing the program.')
    normalize_lights()
    return audio('Paused the stream.').stop()


@ask.intent('AMAZON.StopIntent')
def stop():
    logger.info('Stopping the program.')
    normalize_lights()
    return audio('stopping').clear_queue(stop=True)


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()

@ask.intent('AMAZON.StartOverIntent')
def resume():
    return audio('Resuming.').resume()


if __name__ == '__main__':
    app.run(debug=True)
