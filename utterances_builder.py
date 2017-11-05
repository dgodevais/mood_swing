#!/usr/bin/python
import json
import logging
import yaml

from mood_mapper import MoodMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("utterance_builder")


def create_mood_utterances(config, file_path):
    with open('moods_master.txt', 'r') as f:
        moods = f.readlines()

        mood_mapper = MoodMapper(config)
        for mood in moods:
            mood_mapper.add_synonyms_for_mood_to_mapper(mood)
        for key, val in mood_mapper.mood_mapper.iteritems():
            print key + ": " + val
        with open(file_path, 'w') as f:
            logger.info('Writing the sample utterances file.')
            for mood in mood_mapper.get_all_moods():
                f.write(mood + '\n')


def main():
    logger.info('Starting to build sample utterances.')
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)
        create_mood_utterances(config, './speech_assets/sample_utterances.txt')
    logger.info('Sample utterances complete.')


if __name__ == '__main__':
    main()
