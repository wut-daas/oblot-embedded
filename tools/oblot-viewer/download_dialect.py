import inspect
import os
from json import JSONDecodeError

import pymavlink.dialects.v20 as dialects
from dotenv import load_dotenv
import requests

load_dotenv()

release_info = {
    'api_root': 'https://gitlab.com/api/v4/',
    'project_id': '21991431'
}
target_filename = 'oblot.py'

# noinspection PyTypeChecker
target_dir = os.path.split(os.path.abspath(inspect.getfile(dialects)))[0]
print(f'Dialect will be copied to "{target_dir}"')

query_url = f'{release_info["api_root"]}projects/' \
            f'{release_info["project_id"]}/' \
            f'releases?order_by=released_at&sort=desc'
print(f'Retrieving releases from "{query_url}"')
response = requests.get(query_url)

releases = response.json()
if 'message' in releases:
    print(f'Error: {releases["message"]}')
    exit(1)

if len(releases) == 0:
    print(f'Error: No releases available')
    exit(1)

latest = releases[0]
print(f'Found latest release "{latest["name"]}" with {latest["assets"]["count"]} assets')

dialect_url = ''
for link in latest["assets"]["links"]:
    if link["name"] == target_filename:
        dialect_url = link["direct_asset_url"]
        break
print(f'Retrieving module from "{dialect_url}"')

with open(os.path.join(target_dir, target_filename), 'wb') as outfile:
    headers = {"PRIVATE-TOKEN": os.getenv("TOKEN")}
    response = requests.get(dialect_url, headers=headers)
    try:
        if 'message' in response.json():
            print(f'Error: {response.json()["message"]}')
            print('Currently gitlab.com requires sign in to download assets')
            print('Add a .env file in this directory with contents:')
            print('TOKEN=youraccesstoken')
            exit(1)
    except JSONDecodeError:
        pass  # response was not JSON

    outfile.write(response.content)
print(f'Saved module to "{os.path.join(target_dir, target_filename)}"')
