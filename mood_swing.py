#!/usr/bin/python

import json
import logging
import requests
import time
import unidecode

from concurrent.futures import ThreadPoolExecutor
from flask import Flask
from flask_ask import Ask, statement, question, session, audio
from random import randint
from zappa.async import task

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
ask = Ask(app, "/")

DICT_OFFSET = 1

config = {}
with open('config.json', 'r') as f:
    config = json.load(f)


@ask.launch
def start_skill():
    logger.info('Starting the Mood Swing Alexa skill.')
    start_messages = {
        '0': config['my_name'] + ', what mood are you in?',
        '1': config['my_name'] + ', how are we feeling?',
        '2': 'What are your feels?',
        '3': 'Hi ' + config['my_name'] + ', tell me your mood.'
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
    time.sleep(pause_time)
    requests.post(hue_url, data={})


@ask.intent("FunkyIntent")
def funky():
    logger.info('Hitting the funky intent.')
    speech = "Oh yeah... feeling funky!"
    stream_url = config['funky_music_url']
    hue_url = 'https://maker.ifttt.com/trigger/' + \
        config['funky_ifttt_url'] + '/with/key/' + config['secret_ifttt_key']
    pause_the_lights(hue_url, 1)
    return audio(speech).play(stream_url)


@ask.intent("SexyIntent")
def sexy():
    logger.info('Hitting the sexy intent.')
    speech = 'you got it!'
    sexy_urls = {
        '0': config['get_it_on_music_url'],
        '1': config['sex_you_up_music_url'],
        '2': config['sexual_healing_music_url']
    }
    index = randint(0, len(sexy_urls) - DICT_OFFSET)
    stream_url = sexy_urls[str(index)]
    hue_url = 'https://maker.ifttt.com/trigger/' + \
        config['sexy_ifttt_url'] + '/with/key/' + config['secret_ifttt_key']
    pause_the_lights(hue_url)
    return audio(speech).play(stream_url)


@ask.intent("SadIntent")
def sad():
    logger.info('Hitting the sad intent.')
    speech = 'sorry to hear that'
    stream_url = config['sad_music_url']
    hue_url = 'https://maker.ifttt.com/trigger/' + \
        config['sad_ifttt_url'] + '/with/key/' + config['secret_ifttt_key']
    pause_the_lights(hue_url)
    return audio(speech).play(stream_url)


@ask.intent("SneakyIntent")
def sneaky():
    logger.info('Hitting the sneaky intent.')
    speech = 'shush...'
    stream_url = config['sneaky_music_url']
    hue_url = 'https://maker.ifttt.com/trigger/' + \
        config['sneaky_ifttt_url'] + '/with/key/' + config['secret_ifttt_key']
    pause_the_lights(hue_url)
    return audio(speech).play(stream_url)


@ask.intent('AMAZON.PauseIntent')
def pause():
    logger.info('Pausing the program.')
    requests.post(
        'https://maker.ifttt.com/trigger/' +
        config['normal_ifttt_url'] + '/with/key/' + config['secret_ifttt_key'],
        data={}
    )
    return audio('Paused the stream.').stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()


@ask.intent('AMAZON.StopIntent')
def stop():
    logger.info('Stopping the program.')
    requests.post(
        'https://maker.ifttt.com/trigger/' +
        config['normal_ifttt_url'] + '/with/key/' + config['secret_ifttt_key'],
        data={}
    )
    return audio('stopping').clear_queue(stop=True)


if __name__ == '__main__':
    app.run(debug=True)
