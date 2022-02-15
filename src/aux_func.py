from pathlib import Path
import time
import os
import re
import csv
import requests
import uuid
import src.Sanitizer

DEBUG = True
STRICT_LANG = True
PERF_TEST = False

def valid_lang(code):
	valid_langs = ('en', 'ja')
	is_valid = code in valid_langs
	if STRICT_LANG:
		assert is_valid, f"{code=!r} not in {valid_langs}"
	return is_valid


def zipdir(path, ziph):
	# ziph is zipfile handle
	for root, dirs, files in os.walk(path):
		for file in files:
			ziph.write(os.path.join(root, file), 
					   os.path.relpath(os.path.join(root, file), 
									   os.path.join(path, '..')))

def wait_timer(seconds, msg="waiting..."):
	for i in range(seconds, 0, -1):
		print(f"{msg} ({i})                        ", end="\r")
		time.sleep(1)

# wrap a beautifulSoup tag with wrap_in tag
def wrap(to_wrap, wrap_in):
	contents = to_wrap.replace_with(wrap_in)
	wrap_in.append(contents)

def get_response_content_type(response: requests.Response):
	assert isinstance(response, requests.Response), "to prevent multiple requests, this should only handle Response objects"
	headers = response.headers
	file_type =headers.get('Content-Type', "nope/nope").split("/")[1]
	# Will print 'nope' if 'Content-Type' header isn't found
	assert file_type != 'nope'
	return file_type

cache_setup_complete = False
def setup_cache():
	global cache_setup_complete
	if not cache_setup_complete:
		if not Path("cache").is_dir():
			Path("cache").mkdir()
		if not Path("cache/pages").is_dir():
			Path("cache/pages").mkdir()
		if not Path("cache/images").is_dir():
			Path("cache/images").mkdir()

		try:
			open(Path('cache/images/cache_table.csv'), 'r').close()
		except FileNotFoundError:
			open(Path('cache/images/cache_table.csv'), 'x').close()

# because some dumb sites make their links in the format of '//example.com/...'
def ensure_protocol(url):
	if url[:4] == 'http':
		return url
	elif url[:2] == '//':
		return f'https:{url}'
	elif url[0] == '/':
		print(f"it seems like this incomplete url was run: {url=!r}")
	else:
		raise Exception(f'what in the world is this {url=!r}')

def load_image(url) -> str: #returns filename string with extension, located in cache/images/
	setup_cache()
	url = ensure_protocol(url)

	# need the ass table bc filetypes might not be in url
	with open(Path('cache/images/cache_table.csv'), 'r') as cache_table_file:
		cache_table = list(csv.reader(cache_table_file))
	# print(cache_table)

	to_search = src.Sanitizer.url_to_str_san(url)

	in_cache = None
	input_col = [row[0] for row in cache_table if len(row) == 2]
	if to_search in input_col:
		# already got this image, return cache entry
		index = input_col.index(to_search)
		ret = cache_table[index][1]
		in_cache = ret

		try:
			open(Path(f'cache/images/{ret}'), 'rb').close()
			print(f'\tfound {ret} in cache')
			return ret
		except FileNotFoundError:
			print(f'\t{to_search} found in cache but it\'s entry ({ret}) not saved.')
			print(f'\t\t no worries though, I\'m saving it now')

	attempts = 5
	r = None
	while True:
		attempts += -1
		print(f'\tloading up {url}')
		if attempts < 0:
			raise Exception(f'could not get image at {url}')
		try:
			wait_timer(10, msg='\tfetching image...')
			r = requests.get(url, stream=True)
			if r.status_code == 200:
				break
		except Exception as e:
			print(f'\t - FAILED -  {e}')
			pass

	file_type = get_response_content_type(r)
	assert file_type in ('jpeg', 'png'), f'{url} does not have a valid image type ({file_type})'

	file_name = ""
	if in_cache is None:
		file_name = str(uuid.uuid1()) + '.' + file_type
	else:
		file_name = in_cache
	
	with open(Path('cache/images/cache_table.csv'), 'a') as cache_table_file:
		cache_table_file.write(to_search + ',' + file_name + '\n')

	with open(Path(f'cache/images/{file_name}'), 'wb') as img_file:
		for chunk in r.iter_content(1024):
			img_file.write(chunk)

	return file_name