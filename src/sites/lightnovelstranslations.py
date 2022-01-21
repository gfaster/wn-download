import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.BaseParser import BaseParser
from src.entities.Chapter import Chapter
from src.aux_func import DEBUG
from bs4 import BeautifulSoup, Tag
import re


class LightNovelsTranslations(BaseParser):
	def __init__(self, htmldoc, chapternum):
		super(LightNovelsTranslations, self).__init__(htmldoc, chapternum)

	def _is_next_cptr_link(tag):
		if tag.string == None:
			return False

		out = True
		out = out and tag.name == u"a"								# tag is <a>
		out = out and len(tag.contents) <= 1						# tag has no children
		if tag.parent.get("class") == None:
			return False
		out = out and tag.parent["class"][0] in ("has-text-align-right", "alignright")
		
		out = out and tag.parent.name == "p"
		
		return out

	def get_next_cptr_url(self):
		link = self.c_soup.find_all(LightNovelsTranslations._is_next_cptr_link)
		
		if len(link) == 0:
			return None

		if DEBUG:
			print ("Next Chapter: ", link[0]['href'])
		return link[0]['href']

	def _get_title(self):
		out = self.soup.title.string
		out = re.sub(r'(?i) ?(–|(-+)) ?Light:? ?Novels ?Translations', '', out)
		# out = re.sub(r'^.{0,15} – ', '', out)
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

		# get rid of next and previous chapter links
		for tag in self.c_soup.find_all('div', id='textbox'):
			tag.decompose()

		# get rid of translator tag (no worky)

		for tag in self.c_soup.find_all('p'):
			is_tln = False
			if tag.string == None:
				continue

			# if re.match(r'(?i)(Translator)', tag.string) :
			# 	print(tag.get("style"))
			# 	is_tln = True

			# get rid of tln tag and <hr>s surrounding it
			if is_tln:
				if tag.next_sibling.name == "hr":
					tag.next_sibling.decompose()
				if tag.previous_sibling.name == "hr":
					tag.previous_sibling.decompose()
				tag.decompose()
				break

		# get rid of those pesky empty divs
		for tag in self.c_soup.find_all('div', class_="code-block"):
			tag.decompose()

		for tag in self.c_soup.find_all('div'):
			if tag.get('align') is not None:
				tag.decompose()
