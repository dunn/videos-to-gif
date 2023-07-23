import os, re, json, random
from mastodon import Mastodon

app_name = os.environ['APP_NAME']
api_base = os.environ['API_BASE_URL']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']

client_cred = f'{app_name}_clientcred.secret'
user_cred = f'{app_name}_usercred.secret'

Mastodon.create_app(
    app_name,
    api_base_url = api_base,
    to_file = client_cred,
)

mastodon = Mastodon(client_id = client_cred)
mastodon.log_in(
    username,
    password,
    to_file = user_cred,
)
mastodon = Mastodon(access_token = user_cred)


with open('metadata.json') as f:
    metadata = json.loads(f.read())

selection = random.choice(metadata)
movie_title = os.environ['MOVIE_TITLE']

attachment = mastodon.media_post(
    selection['path'],
    description = f'{movie_title} gif; subtitles read "{selection["text"]}"',
    synchronous = True,
)

mastodon.status_post(
    selection['text'],
    media_ids = [attachment['id']],
)
