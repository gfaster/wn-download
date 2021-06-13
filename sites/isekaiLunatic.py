import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from bs4 import BeautifulSoup, Tag
import re


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
			if DEBUG:
				print("no next chapter")
			return None

		if DEBUG:
			print ("Next Chapter: ", link[0]['href'])
		return link[0]['href']

	def _get_title(self):
		out = self.soup.title.string
		out = re.sub(r' ?(–|(-+)) ?Reigokai: ?Isekai ?Translations', '', out)
		out = re.sub(r'^.{0,15} – ', '', out)
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

		for sharelink in self.c_soup.find_all('div', class_='sharedaddy'):
			sharelink.decompose()

		for tag in self.c_soup.find_all('p'):
			is_nav = False
			for child in tag.contents:
				if child.string == None:
					continue
				if isinstance(child, Tag) and re.match(r'(?i)(next)|(previous) chapter', child.string):
					is_nav = True
			if is_nav:
				tag.decompose()
				break


