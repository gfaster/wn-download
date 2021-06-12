from pathvalidate import sanitize_filename
import html
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup
import os
import re



class BaseParser(object):
	"""class that all parsers should inherit from"""
	def __init__(self, htmldoc, chapternum):
		super(BaseParser, self).__init__()
		self.htmldoc = htmldoc
		self.chapternum = chapternum
		self.soup = BeautifulSoup(htmldoc, "html.parser")
		self._set_c_soup()

	def _set_c_soup(self):
		self.c_soup = self.soup.find(class_="entry-content")
		assert self.c_soup

	def get_chapter_title(self):
		return self.soup.title.string

	def get_next_cptr_url(self):
		return None

	def get_content(self):
		return self.c_soup.get_text()

	def cleanup_content(self):

		# get rid of all scripts
		while self.c_soup.script is not None:
			self.c_soup.script.decompose()


		# convert style italics to html tags
		def style_italic(tag):
			out = True
			out = out and tag.get('style') is not None
			out = out and re.search(r"font-style: ?(italic)|(oblique)", tag.get('style'))
			return out

		for tag in self.c_soup.find_all(style_italic):
			wrap(tag, self.c_soup.new_tag("em"))


		# convert style bold to html tags
		def style_bold(tag):
			out = True
			out = out and tag.get('style') is not None
			out = out and re.search(r"font-weight: ?(bold(er)?)|([5-9]##)", tag.get('style'))
			return out

		for tag in self.c_soup.find_all(style_bold):
			wrap(tag, self.c_soup.new_tag("strong"))


		# get rid of all style tags
		for tag in self.c_soup.find_all(True, attrs={"style": True}):
			del tag['style']



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

def cmd_exec(cmd):
	print(cmd)
	os.system(cmd)

# wrap a beautifulSoup tag with wrap_in tag
def wrap(to_wrap, wrap_in):
    contents = to_wrap.replace_with(wrap_in)
    wrap_in.append(contents)