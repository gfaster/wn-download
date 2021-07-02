import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from bs4 import BeautifulSoup, Tag
import re
import html5lib

class Skythewood(BaseParser):
	prints = 1

	def __init__(self, htmldoc, chapternum):
		super(Skythewood, self).__init__(htmldoc, chapternum)
		self.include_images = True

		self.soup = BeautifulSoup(htmldoc, "html5lib")
		self._set_c_soup()


	# def __init__(self, htmldoc, chapternum):

		# basically this site has unescapped tl/n's, this is a shitty fix
		# but maybe not?? the output has unescapped shit soooooo?
		# magic_regex = r'<(?!html|head|span|div|script|a|/|body|br|canvas|p|\!DOCTYPE|\!\-|header
		#|title|meta|h1|h2|h3|h4|b|i|em|strong|style|link|ol|ul|li|hr|footer|cite|table|tbody|tr|td|form)(?! )(.*)?>'
		# new_doc = re.sub(magic_regex, '[\2]', htmldoc)

		# super(Skythewood, self).__init__(htmldoc, chapternum)
		# if Skythewood.prints > 0:
		# 	print(self.soup.get_text())
		# 	Skythewood.prints -= 1

	def _is_next_cptr_link(tag):
		out = True
		out = out and tag.name == 'a'
		out = out and tag.string == "Next Chapter"
		return out

	def get_next_cptr_url(self):
		out = self.c_soup.find_all(Skythewood._is_next_cptr_link)
		if len(out) == 0 and DEBUG:
			print("No next chapter")
		if len(out) == 0:
			return None
		return out[0]['href']


	def cleanup_content(self):
		
		for tag in self.c_soup.find_all('div'):

			# seems like this sites <p> replacement
			if tag.get('dir') == 'ltr':
				del tag['dir']
				tag.name = 'p'

				if re.search(r'Next Chapter', tag.get_text()) is not None:
					tag.decompose()



		for tag in self.c_soup.find_all(class_="seperator"):
			tag.decompose()


		super().cleanup_content()


		

		for span in self.c_soup.find_all('span'):
			span.unwrap()

		if Skythewood.prints > 0:
			# print(self.c_soup.prettify())
			Skythewood.prints -= 1



