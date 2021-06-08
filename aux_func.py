from pathvalidate import sanitize_filename
import html
from urllib.parse import urlparse
import time

def file_san(string):
	out = sanitize_filename(string)
	return out.replace(r".", "_")

def san(string):
	no_q = html.escape(string).replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c","\"").replace(u"\u201d", "\"")
	# return re.sub(r'(?=[^\w\-_\. \[\]\(\)\?\<\>…\/,\%\$\#\!\~])(?=^"\n")', ' ',no_q)
	# return html.escape(html.unescape(string))
	# return string
	return no_q

def get_site(url):
	t = urlparse(url).netloc
	return t.split('www.')[-1].split('.')[0]

def wait_timer(seconds, msg="waiting..."):
	for i in range(seconds, 0, -1):
		print(f"{msg} ({i})    ", end="\r")
		time.sleep(1)
