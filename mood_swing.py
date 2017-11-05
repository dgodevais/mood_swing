#!/usr/bin/python

import logging
import time
import yaml
from random import randint

import requests
from flask import Flask
from flask_ask import Ask, question, audio
from mood_mapper import MoodMapper
from zappa.async import task

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
ask = Ask(app, "/")

DICT_OFFSET = 1

config = {}
with open('config.yaml', 'r') as f:
    config = yaml.load(f)

mood_mapper = MoodMapper(config)
starter_moods = mood_mapper.get_all_moods()
for starter_mood in starter_moods:
    mood_mapper.add_synonyms_for_mood_to_mapper(starter_mood)

mood_to_music_url_map = mood_mapper.mood_to_music_url_mapper
mood_to_hue_map = mood_mapper.mood_to_hue_mapper


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


@task
def pause_the_lights(hue_url, pause_time=2):
    logger.info("calling lights: {}".format(hue_url))
    time.sleep(pause_time)
    requests.post(hue_url, data={})


@ask.intent("MoodIntent")
def set_the_mood(my_mood):
    speech = "Setting the mood to {}".format(my_mood)
    logger.info(speech)
    if my_mood in mood_to_hue_map and my_mood in mood_to_music_url_map:
        stream_url = mood_to_music_url_map[my_mood]
        hue_url = mood_to_hue_map[my_mood]
        pause_the_lights(hue_url, 1)
        return audio(speech).play(stream_url)
    else:
        logger.info('{} not found in mood mapper'.format(my_mood))
        return stop()


@ask.intent('AMAZON.PauseIntent')
def pause():
    logger.info('Pausing the program.')
    requests.post(config['ifttt']['normal_url'], data={})
    return audio('Paused the stream.').stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()


@ask.intent('AMAZON.StopIntent')
def stop():
    logger.info('Stopping the program.')
    requests.post(config['ifttt']['normal_url'], data={})
    return audio('stopping').clear_queue(stop=True)


if __name__ == '__main__':
    app.run(debug=True)
