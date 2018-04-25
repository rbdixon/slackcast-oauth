import os
import logging
import requests

from urllib.parse import urlparse, parse_qs
from flask import Flask, redirect, request

__all__ = ['app']

app = Flask(__name__)
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

SLACK_AUTH_URL = 'https://slack.com/oauth/authorize'
SLACK_TOKEN_URL = 'https://slack.com/api/oauth.access'
CLIENT_ID = os.environ['SLACKCAST_CLIENT_ID']
CLIENT_SECRET = os.environ['SLACKCAST_CLIENT_SECRET']
SCOPE = 'channels:read chat:write:bot chat:write:user im:read im:write users:read'
STAGE = os.environ.get('STAGE', 'dev')

if STAGE == 'prod':
    PREFIX = ''
    REDIRECT_URI = 'https://slackcast.devtestit.com/redirect'
else:
    PREFIX = '/dev'
    REDIRECT_URI = f'https://1ixagcdjk7.execute-api.us-east-1.amazonaws.com{PREFIX}/redirect'

def get_state():
    return 'foo'

def valid_state(state):
    return state == 'foo'

def get_token(code):
    res = requests.get(SLACK_TOKEN_URL, params={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
        })

    payload = res.json()
    log.debug(f'Slack says: {res.status_code} {res.reason}: {payload.get("error", "No error message.")}')

    if not (res.ok and payload['ok']): return

    return payload.get('access_token', None)

@app.route('/', methods=['GET'])
def index():
    return f'''
<html>
<head>
<title>Slackcast - Mirror IPython and Jupyter sessions to Slack</title>
</head>
<body>
<h1>Slackcast</h1>
<p>Mirror IPython and Jupyter sessions to Slack</p>
<p><a href="https://github.com/rbdixon/slackcast">Installation instructions</a></p>
<p>
<a href="{PREFIX}/install"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>
</p>
</body>
</html>
'''


@app.route('/install', methods=['GET'])
def start_install(event=None, context=None):
    log.info('Redirecting to Slack OAuth2 authorize URL.')

    return redirect(f'{SLACK_AUTH_URL}?client_id={CLIENT_ID}&scope={SCOPE}&state={get_state()}&redirect_uri={REDIRECT_URI}')

@app.route('/redirect', methods=['GET'])
def extract_token(event=None, context=None):
    log.info('Extracting authorization token from redirect URL.')

    params = parse_qs(urlparse(request.url).query)

    state = params.get('state', [None])[0] 
    code = params.get('code', [None])[0]

    if code is None:
        return 'No authorization code received from Slack.'

    if not valid_state(state):
        return 'Invalid state.'

    token = get_token(code)

    if token is not None:
        return token
    else:
        return 'Unauthorized', 401

if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.7', port=65000)
