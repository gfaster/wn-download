from pathvalidate import sanitize_filename
import html
from urllib.parse import urlparse
import time
import urllib.request
from bs4 import BeautifulSoup
import os
import re
import sys
from dataclasses import dataclass, field


DEBUG = False
sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations"]

@dataclass(order=True, frozen=True)
class Chapter(object):
	"""Class that all parsers should return """
	number: int = field(repr=False)
	title: str
	content: str = field(repr=False)

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

	def get_content(self) -> Chapter:
		out = Chapter(number = self.chapternum, title = self.soup.title.string, content = self.c_soup.get_text())
		return out

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
		for tag in self.c_soup.find_all('img'):
			tag.decompose()


		# get rid of empty divs
		def empty_div(tag):
			out = True
			out = out and tag.name in ('div', 'span')
			out = out and len(tag.get_text(strip = True)) == 0

		for tag in self.c_soup.find_all(empty_div):
			tag.decompose()


from sites.wuxiaWorld import *
from sites.isekaiLunatic import *
from sites.lightnovelstranslations import *




@dataclass(order=True)
class Section(object):
	title: str
	first_chapter_url: str = field(repr=False)
	final_chapter_url: str = field(repr=False)
	chapter_list: list = field(repr=False, init=False)
	file_title:str = field(init=False)

	def __post_init__(self):
		self.file_title = file_san(self.title).replace(" ", "_")
		self.chapter_list = list()

	def generate_html(self) -> str:
		url = self.first_chapter_url
		html = """<?xml version="1.0" encoding="UTF-8"?>
				<!DOCTYPE html>
				<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"
					xml:lang="en" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#">
					<head>
						<title>{}</title>
						<link href="css/epub.css" type="text/css" rel="stylesheet" />
					</head><body>""".format(self.title)
		count = 1
		max_count = 3000
		parser_type = get_parser(url)
		if DEBUG:
			max_count = 5

		while url is not None and count <= max_count:

			parser = parser_type(load_site(url=url), count)
			next_url = parser.get_next_cptr_url()

			chapter = parser.get_content()
			assert len(chapter.content) > 0
			html += f"<section id=\"{hash(chapter)}\">"
			html += chapter.content
			html += "</section>"

			if url == self.final_chapter_url:
				break
			assert len(html) < 4000000, "Section is too long"

			self.chapter_list.append(chapter)
			url = next_url
			count += 1
		html += "</body></html>"
		# print(html)
		return html


class Book(object):
	"""Stores all chapter links and sections for chapters"""
	def __init__(self, title):
		super(Book, self).__init__()
		self.title = file_san(title)
		self.sections = list()

	def append(self, section:Section):
		assert isinstance(section, Section)
		assert section.file_title not in [s.file_title for s in self.sections], "non-unique title"
		self.sections.append(section)

	def __iter__(self):
		return self.sections.__iter__()

	def __len__(self):
		return len(self.sections)





def get_parser(url):
	c_url = get_site(url).casefold()
	c_sites = [x.casefold() for x in sites]
	# print(f"Site is: {c_url}")
	assert c_url in c_sites, " If this raises, the site is unimplemented"
	parser_class_name = sites[c_sites.index(c_url)]

	# gets the parser class located in the [site].py 
	ret = getattr(sys.modules[__name__], parser_class_name)
	assert issubclass(ret, BaseParser), f"{parser_class_name} does not inherit from BaseParser"
	return ret

def load_site(url=""):
	ret = ""
	try:
		# try and get the file from the cache if it exists
		f = open(f"cache\\{file_san(url)}.html", "r", encoding='utf-8')
		print(f"found {file_san(url)} in cache")
		ret = f.read()
		f.close()
	except:
		wait_timer(10)
		print("loading up ",url)
		req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		ret = urllib.request.urlopen(req).read().decode("UTF-8")
		f = open(f"cache\\{file_san(url)}.html", "w", encoding='utf-8')
		f.write(ret)
		f.close()

	# print (type (ret))
	return ret.replace(r"&nbsp;", " ")

def gen_nav(book:Book):
	# <?xml version="1.0" encoding="utf-8"?>
	# had this xml line in there but it didn't like it?
	header = """ 
	<!DOCTYPE html>
	<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en"
	lang="en">
	<head>
		<title>{}</title>
		<link href="css/epub.css" rel="stylesheet" type="text/css"/>
		<link href="css/nav.css" rel="stylesheet" type="text/css"/>
	</head>
	<body>
	<nav epub:type="toc" id="toc">
	<h2>Contents</h2>
	
	</nav>
	</body>
	</html>
	""".format(book.title)
	# <ol id="tocList">
	# </ol>

	soup = BeautifulSoup(header,features="lxml")

	section_list = soup.new_tag("ol")
	soup.nav.append(section_list)
	for section in book:
		section_li = soup.new_tag("li")
		section_ol = soup.new_tag("ol", id=f"{section.file_title}List")

		last_chap = None
		for chapter in section.chapter_list:
			line = soup.new_tag("li")
			line.append(soup.new_tag("a", href=f"{section.file_title}.xhtml#{hash(chapter)}"))
			line.a.string = chapter.title
			section_ol.append(line)
			last_chap = chapter

		section_h2 = soup.new_tag("a", href=f"{section.file_title}.xhtml#{hash(last_chap)}")
		section_h2.string = section.title
		section_list.append(section_li)
		section_li.append(section_h2)
		section_li.append(section_ol)

	# out = header
	# for section in book:
	# 	for chapter in section.chapter_list:
	# 		assert isinstance(chapter, Chapter)
	# 		assert isinstance(chapter.number, (int, float))
	# 		out += line.format(hash(chapter), chapter.title)
	# out += footer

	return soup.prettify()


def modify_opf(book:Book):
	soup = None
	with open('epub_template/dynamic_files/package.opf', 'r') as opf:
		soup = BeautifulSoup(opf.read(), "xml")

	main_title = soup.find('dc:title', id='t1')
	main_title.string = book.title

	sub_title = soup.find('dc:title', id='t2')
	sub_title.string = book.title.strip() + " Created with WN-Download"

	# <item href="s04.xhtml" id="s04" media-type="application/xhtml+xml"/>
	# <itemref idref="s04"/>
	# add sections files
	for section in book:
		new_tag = soup.new_tag("item", attrs={'href':f"{section.file_title}.xhtml", 'id':section.file_title, 'media-type': 'application/xhtml+xml'})
		soup.manifest.append(new_tag)

		new_tag = soup.new_tag("itemref", idref=section.file_title)
		soup.spine.append(new_tag)


	return soup.prettify()	

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def file_san(string):
	out = sanitize_filename(string)
	out = out.replace(".", "_")
	stripped = (c for c in out if 0 < ord(c) < 127)
	return ''.join(stripped)

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