import inspect
import os

import pymavlink.dialects.v20 as dialects
import requests

release_url = 'https://github.com/wut-daas/oblot-embedded/releases/latest/download/oblot.py'
target_filename = 'oblot.py'

# noinspection PyTypeChecker
target_dir = os.path.split(os.path.abspath(inspect.getfile(dialects)))[0]
print(f'Dialect will be copied to "{target_dir}"')

with open(os.path.join(target_dir, target_filename), 'wb') as outfile:
    print(f'Downloading generated Python dialect from "{release_url}"')
    response = requests.get(release_url, allow_redirects=True)
    bytecount = outfile.write(response.content)
    print(f'Written {bytecount} bytes')

print(f'Saved module to "{os.path.join(target_dir, target_filename)}"')
