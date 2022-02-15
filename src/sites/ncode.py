import os, sys
from src.entities.Chapter import Chapter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.BaseParser import BaseParser
from bs4 import BeautifulSoup, Tag
import re
from src.aux_func import DEBUG


class Ncode(BaseParser):
	prints = 1
	def __init__(self, htmldoc, chapternum):
		super(Ncode, self).__init__(htmldoc, chapternum)
		self.include_images = True

	def _set_c_soup(self):
		self.c_soup = self.soup.find(id="novel_honbun") # 本文 = text body
		del self.c_soup['id']
		self.c_soup['class'] = "entry-content"
		assert self.c_soup

	def _is_next_cptr_link(tag):
		if tag.string == None:
			return False

		out = True
		out = out and tag.name == u"a"								# tag is <a>
		out = out and len(tag.contents) <= 1						# tag has no children
		out = out and len(tag.string) < 30							# tag isn't too long (to reduce searching)
		out = out and re.search(r"次へ >>", tag.string)			# tag contents contain next chapter
		return out


	def get_next_cptr_url(self):
		search_soup = self.soup.find(id="novel_contents")
		link = search_soup.find_all(Ncode._is_next_cptr_link)
		
		if len(link) == 0:
			if DEBUG:
				print("no next chapter")
			return None

		out = f"https://ncode.syosetu.com{link[-1]['href']}"

		if DEBUG:
			print ("Next Chapter: ", out)
		return out

	def _get_title(self):
		out = self.soup.find(class_="novel_subtitle").string
		return out


	def get_content(self):
		self.cleanup_content()

		# holy shit this notation is ugly but class_ will actually put in "class_" instead of "class"
		chapter_h1 = self.soup.new_tag('h2', **{'class':'chapter-heading'})
		self.c_soup.insert(0, chapter_h1)
		chapter_h1.string = self._get_title()
		out = Chapter(number = self.chapternum, title = self._get_title(), content = self.c_soup.prettify(),images = self.images)

		return out

	def cleanup_content(self):
		super().cleanup_content()

		for tag in self.c_soup.find_all('p'):
			del tag['id']

		for tag in self.c_soup.find_all('blockquote'):
			print(f"removing blockquote containing: {tag.get_text()}")
			tag.decompose()


