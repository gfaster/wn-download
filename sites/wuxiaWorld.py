import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from bs4 import BeautifulSoup, Tag
import re


class WuxiaWorld(BaseParser):
	def __init__(self, htmldoc, chapternum):
		super(WuxiaWorld, self).__init__(htmldoc, chapternum)

	def _set_c_soup(self):
		self.c_soup = self.soup.find(id="chapter-content")
		assert self.c_soup

	def _is_next_cptr_link(tag):

		out = True
		out = out and tag.name == u"a"								# tag is <a>
		out = out and len(tag.contents) >= 1						# tag has children
		if tag.img == None:
			return False
		out = out and tag.img.get("alt") == "newer"
		
		return out

	def get_next_cptr_url(self):
		link = self.soup.find_all(WuxiaWorld._is_next_cptr_link)
		
		if len(link) == 0:
			if DEBUG:
				print("No next link")
			return None

		if not re.match(r'(?i)wuxiaworld', link[0]['href']):
			link[0]['href'] = "https://www.wuxiaworld.com" + link[0]['href']

		if DEBUG:
			print ("Next Chapter: ", link[0]['href'])
		return link[0]['href']

	def _get_title(self):
		out = self.soup.title.string
		out = re.sub(r'(?i) ?- WuxiaWorld', '', out)
		out = re.sub(r'^.{0,15} - ', '', out)
		return out


	def get_content(self):
		self.cleanup_content()

		# holy shit this notation is ugly but class_ will actually put in "class_" instead of "class"
		chapter_h1 = self.soup.new_tag('h2', **{'class':'chapter-heading'})
		self.c_soup.insert(0, chapter_h1)
		chapter_h1.string = self._get_title()

		out = Chapter(number = self.chapternum, title = self._get_title(), content = self.c_soup.prettify())

		return out

	def cleanup_content(self):
		super().cleanup_content()

		for tag in self.c_soup.find_all("p"):
			if tag.get("dir") is not None:
				del tag["dir"]
			if tag.contents[0].name == "span":
				tag.contents[0].unwrap()

		for tag in self.c_soup.find_all("a", class_="chapter-nav"):
			tag.decompose()
