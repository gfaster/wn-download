from bs4 import BeautifulSoup
import re
from src.entities.Chapter import Chapter
from src.aux_func import *


class BaseParser(object):
	"""class that all parsers should inherit from"""
	def __init__(self, htmldoc, chapternum):
		super(BaseParser, self).__init__()
		self.htmldoc = htmldoc
		self.chapternum = chapternum
		self.soup = BeautifulSoup(htmldoc, "html.parser")
		self._set_c_soup()
		self.has_cleaned = False
		self.include_images = False
		self.images = set()

	def _set_c_soup(self):
		self.c_soup = self.soup.find(class_="entry-content")
		assert self.c_soup

	def get_chapter_title(self):
		return self.soup.title.string

	def get_next_cptr_url(self):
		return None

	def get_content(self) -> Chapter:
		self.cleanup_content()
		out = Chapter(number = self.chapternum, title = self.soup.title.string, content = self.c_soup.prettify(), images = self.images)
		return out

	def cleanup_content(self):
		if self.has_cleaned:
			return

		# get rid of all scripts
		while self.c_soup.script is not None:
			self.c_soup.script.decompose()
		# Remove Iframes as most ereaders won't have internet
		while self.c_soup.iframe is not None:
			print(f"Removed iframe in {self.chapternum}")
			self.c_soup.iframe.decompose()
		
		# convert style italics to html tags
		def style_italic(tag):
			out = True
			out = out and tag.get('style') is not None
			out = out and re.search(r"font-style: ?(italic)|(oblique)", tag.get('style'))
			return out

		for tag in self.c_soup.find_all(style_italic):
			tag.wrap(self.soup.new_tag("i"))


		# convert style bold to html tags
		def style_bold(tag):
			out = True
			out = out and tag.get('style') is not None
			out = out and re.search(r"font-weight: ?(bold(er)?)|([5-9]##)", tag.get('style'))
			return out

		for tag in self.c_soup.find_all(style_bold):
			tag.wrap(self.soup.new_tag("b"))


		# get rid of all style tags
		for tag in self.c_soup.find_all(True, attrs={"style": True}):
			del tag['style']


		# TODO: Support images
		# get rid of all img tags
		if self.include_images:
			for tag in self.c_soup.find_all('img'):
				img = None
				if ".gif" in tag['src']:
					tag.decompose()
					continue;
				try:
					img = load_image(tag['src'])
					self.images |= set((img,))
					for attr in list(tag.attrs):
						del tag[attr]
					tag['src'] = f'images/{img}'
					tag['role'] = 'presentation'
				except Exception as e:

					print(f'failed to get image at' + tag.get('src'))
					raise e

				
		else:
			for tag in self.c_soup.find_all('img'):
				if DEBUG:
					print('removed image')
				tag.decompose()



		# get rid of empty tags
		def empty_div(tag):
			out = True
			out = out and tag.name in ('div', 'span', 'b', 'em', 'strong', 'i', 'a')
			out = out and len(tag.get_text(strip = True)) == 0
			return out

		for tag in self.c_soup.find_all(empty_div):
			if self.include_images and tag.img is not None:
				tag.unwrap()
			else:
				tag.decompose()


		# we use <p> tags, so we don't need line breaks
		for tag in self.c_soup.find_all('br'):
			tag.decompose()

		self.has_cleaned = True

