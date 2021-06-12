import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from bs4 import BeautifulSoup
import re

DEBUG = True

class IsekaiLunatic(BaseParser):
	def __init__(self, htmldoc, chapternum):
		super(IsekaiLunatic, self).__init__(htmldoc, chapternum)

	def _is_next_cptr_link(tag):
		if tag.string == None:
			return False

		out = True
		out = out and tag.name == u"a"								# tag is <a>
		out = out and len(tag.contents) <= 1						# tag has no children
		out = out and len(tag.string) < 30							# tag isn't too long (to reduce searching)
		out = out and re.search(r"(?i)next ?chapter", tag.string)	# tag contents contain next chapter
		return out

	def get_next_cptr_url(self):
		link = self.c_soup.find_all(IsekaiLunatic._is_next_cptr_link)
		
		if len(link) == 0:
			return None

		if DEBUG:
			print ("Next Chapter: ", link[0]['href'])
		return link[0]['href']

	def get_content(self):
		self.cleanup_content()

		chapter_h1 = self.soup.new_tag('h1', class_='chapter-heading')
		self.c_soup.insert(0, chapter_h1)
		chapter_h1.string = f"Chapter {self.chapternum}"

		return self.c_soup.prettify()

	def cleanup_content(self):
		super().cleanup_content()

		for sharelink in self.c_soup.find_all('div', class_='sharedaddy'):
			sharelink.decompose()
