import html
import re
from urllib.parse import urlparse
from pathvalidate import sanitize_filename

from src.aux_func import *
sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations", "Skythewood"]
def get_site(url):
	assert isinstance(url, str)
	t = urlparse(url).netloc
	t = t.split('www.')
	return t[-1].split('.')[0]

def file_san(string):
	out = sanitize_filename(string)
	out = out.replace(".", "_")
	out = out.replace(",", "_")
	out = out.replace('=', '-')
	stripped = (c for c in out if 0 < ord(c) < 127)
	return ''.join(stripped)

def url_to_str_san(url):
	t = urlparse(url)
	pre = get_site(url)
	post = t.path

	assert pre
	assert post
	out = file_san(pre + post)

	assert out
	return out	

def san(string):
	no_q = html.escape(string).replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c","\"").replace(u"\u201d", "\"")
	# return re.sub(r'(?=[^\w\-_\. \[\]\(\)\?\<\>…\/,\%\$\#\!\~])(?=^"\n")', ' ',no_q)
	# return html.escape(html.unescape(string))
	# return string
	return no_q

def hyper_san(string):
	return re.sub(r'[^a-zA-Z]', '', string)