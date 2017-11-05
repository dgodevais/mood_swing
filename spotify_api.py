import base64
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spotify_api")


class SpotifyApi:
    def __init__(self, config_json):
        self.config = config_json

    def get_access_token(self):
        logger.info('Getting access token from spotify api')
        client_secret = self.config['spotify_client_secret']
        client_id = self.config['spotify_client_id']
        url = 'https://accounts.spotify.com/api/token'
        authorization = base64.standard_b64encode(client_id + ':' + client_secret)
        headers = {'Authorization': 'Basic ' + authorization}
        data = {'grant_type': 'client_credentials'}
        try:
            resp = requests.post(url, headers=headers, data=data)
            data = json.loads(resp.text)
            return data['access_token']
        except requests.RequestException as e:
            logger.error('Request failed: ' + str(e))
        except ValueError as e:
            logger.error('Request failed: ' + str(e))
        except KeyError as e:
            logger.error('Request failed: ' + str(e))

    def get_song_preview_url(self):
        url = 'https://api.spotify.com/v1/tracks/5uuJruktM9fMdN9Va0DUMl'
        headers = {'Authorization': 'Bearer ' + self.get_access_token()}
        try:
            resp = requests.get(url, headers=headers)
            data = json.loads(resp.text)
            return data['preview_url']
        except requests.RequestException as e:
            logger.error('RequestException: ' + str(e))
        except ValueError as e:
            logger.error('ValueError: ' + str(e))
        except KeyError as e:
            logger.error('KeyError: ' + str(e))


def main():
    logger.info('Starting to build sample utterances.')
    with open('config.json', 'r') as f:
        config = json.load(f)
        spotify = SpotifyApi(config)
        song_preview = spotify.get_song_preview_url()
        print song_preview
    logger.info('Spotify API complete.')


if __name__ == '__main__':
    main()
