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
from urllib.request import urlopen
import csv
import requests
import uuid


DEBUG = False
sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations", "Skythewood"]

@dataclass(order=True, frozen=True)
class Chapter(object):
	"""Class that all parsers should return """
	number: int = field(repr=False)
	title: str
	content: str = field(repr=False)
	images: set = field(default_factory=set, repr=False, hash=False, compare=False)



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

				try:
					img = load_image(tag['src'])
					self.images |= set((img,))
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


from sites.wuxiaWorld import *
from sites.isekaiLunatic import *
from sites.lightnovelstranslations import *
from sites.skythewood import *




@dataclass(order=True)
class Section(object):
	title: str
	first_chapter_url: str = field(repr=False)
	final_chapter_url: str = field(repr=False)
	chapter_list: list = field(repr=False, init=False)
	file_title:str = field(init=False)
	images: set = field(init=False, repr=False, hash=False)

	def __post_init__(self):
		self.file_title = file_san(self.title).replace(" ", "_")
		self.chapter_list = list()
		self.images = set()
		assert self.first_chapter_url != "", "no first chapter url"
		assert self.final_chapter_url != "", "no final chapter url"

	def get_images(self):
		for chapter in self.chapter_list:
			self.images |= chapter.images
		return self.images

	def generate_html(self) -> str:
		url = self.first_chapter_url
		assert url != "", "url is blank"
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
			html += f"<section id=\"{ghash(chapter)}\">"
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

	def get_images(self):
		images = set()
		for section in self.sections:
			images |= section.get_images()
		return images

		





def get_parser(url):
	c_url = get_site(url).casefold()
	c_sites = [x.casefold() for x in sites]
	# print(f"Site is: {c_url}")
	assert c_url in c_sites, "{} is not in the sites list".format(c_url)
	parser_class_name = sites[c_sites.index(c_url)]

	# gets the parser class located in the [site].py 
	ret = getattr(sys.modules[__name__], parser_class_name)
	assert issubclass(ret, BaseParser), f"{parser_class_name} does not inherit from BaseParser"
	return ret

def load_site(url=""):
	ret = ""
	try:
		# try and get the file from the cache if it exists
		f = open(f"cache\\{url_to_str_san(url)}.html", "r", encoding='utf-8')
		print(f"found {url_to_str_san(url)} in cache")
		ret = f.read()
		f.close()
	except:
		continue_flag = False
		tries_left = 5
		while not continue_flag:
			wait_timer(10)
			print("loading up ",url)
			req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (epub scraper)'})
			try:
				ret = urllib.request.urlopen(req).read().decode("UTF-8")
				continue_flag = True
			except:
				tries_left -= 1
				print("FAILED TO LOAD:", url)
			if tries_left <= 0:
				raise Exception("ran out of attempts")
				
		f = open(f"cache\\{url_to_str_san(url)}.html", "w", encoding='utf-8')
		f.write(ret)
		f.close()

	# print (type (ret))
	return ret

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
			line.append(soup.new_tag("a", href=f"{section.file_title}.xhtml#{ghash(chapter)}"))
			line.a.string = chapter.title
			section_ol.append(line)
			last_chap = chapter

		section_h2 = soup.new_tag("a", href=f"{section.file_title}.xhtml#{ghash(last_chap)}")
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

def modify_ncx(book:Book):
	soup = None
	with open('epub_template/dynamic_files/toc.ncx', 'r') as ncx:
		soup = BeautifulSoup(ncx.read(), "xml")

	soup.docTitle.find('text').string = book.title

	playorder_index = 1
	for section in book:
		sec_navpoint = soup.new_tag('navPoint', attrs={'class':'section', 'id':hyper_san(section.file_title), 'playOrder':str(playorder_index)})
		sec_navpoint_navlabel = soup.new_tag('navLabel')
		sec_navpoint.append(sec_navpoint_navlabel)

		sec_navpoint_text = soup.new_tag('text')
		sec_navpoint_text.string = section.title
		sec_navpoint_navlabel.append(sec_navpoint_text)

		sec_navpoint_content = soup.new_tag('content')
		sec_navpoint_content['src'] = f"{section.file_title}.xhtml"
		sec_navpoint.append(sec_navpoint_content)

		soup.navMap.append(sec_navpoint)
		playorder_index += 1

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
		new_tag = soup.new_tag("item", attrs={'href':f"{section.file_title}.xhtml", 'id':hyper_san(section.file_title), 'media-type': 'application/xhtml+xml'})
		soup.manifest.append(new_tag)

		new_tag = soup.new_tag("itemref", idref=hyper_san(section.file_title))
		soup.spine.append(new_tag)

	for image in book.get_images():
		assert isinstance(image, str)
		img_type = image.split('.')[-1]

		new_tag = soup.new_tag("item", attrs={'href':f"images/{image}", 'id':hyper_san(image), 'media-type': f'image/{img_type}'})
		soup.manifest.append(new_tag)


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
	out = out.replace(",", "_")
	out = out.replace('=', '-')
	stripped = (c for c in out if 0 < ord(c) < 127)
	return ''.join(stripped)

def url_to_str_san(url, do_hash=False):
	t = urlparse(url)
	pre = get_site(url)
	post = t.path

	out = None
	assert pre
	assert post

	if do_hash:
		out = file_san(pre + ghash(post))
	else:
		out = file_san(pre + post)

	assert out
	return out	

def san(string):
	no_q = html.escape(string).replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c","\"").replace(u"\u201d", "\"")
	# return re.sub(r'(?=[^\w\-_\. \[\]\(\)\?\<\>…\/,\%\$\#\!\~])(?=^"\n")', ' ',no_q)
	# return html.escape(html.unescape(string))
	# return string
	return no_q

def hyper_san(string):
	return re.sub(r'[^a-zA-Z]', '', string)

def get_site(url):
	assert isinstance(url, str)
	t = urlparse(url).netloc
	t = t.split('www.')
	return t[-1].split('.')[0]

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

def get_file_extension(file: str):
	out = re.search(r'\.[a-zA-Z]{1,5}')
	if out is not None:
		return out.group(1)
	else:
		raise Exception(f"{file} has no extension")

def get_response_content_type(response: requests.Response):
	assert isinstance(response, requests.Response), "to prevent multiple requests, this should only handle Response objects"
	headers = response.headers
	file_type =headers.get('Content-Type', "nope/nope").split("/")[1]
	# Will print 'nope' if 'Content-Type' header isn't found
	assert file_type != 'nope'
	return file_type


def ghash(obj):
	return hex(abs(hash(obj)))[2:]


def load_image(url) -> str: #returns filename string with extension, located in cache/images/

	# need the ass table bc filetypes might not be in url
	try:
		open('cache\\images\\cache_table.csv', 'r').close()
	except:
		open('cache\\images\\cache_table.csv', 'x').close()

	with open('cache\\images\\cache_table.csv', 'r') as cache_table_file:
		cache_table = list(csv.reader(cache_table_file))
	# print(cache_table)

	to_search = url_to_str_san(url, do_hash=False)

	in_cache = None
	input_col = [row[0] for row in cache_table if len(row) == 2]
	if to_search in input_col:
		# already got this image, return cache entry
		index = input_col.index(to_search)
		ret = cache_table[index][1]
		in_cache = ret

		try:
			open(f'cache\\images\\{ret}', 'rb').close()
			print(f'\tfound {ret} in cache')
			return ret
		except:
			print(f'\t{to_search} found in cache but it\'s entry ({ret}) not saved.')
			print(f'\t\t no worries though, I\'m saving it now')

	attempts = 5
	r = None
	while True:
		attempts += -1
		print(f'\tloading up  {url}')
		if attempts < 0:
			raise Exception(f'could not get image at {url}')
		try:
			wait_timer(10, msg='\tfetching image...')
			r = requests.get(url, stream=True)
			if r.status_code == 200:
				break
		except:
			pass
		

	file_type = get_response_content_type(r)
	assert file_type in ('jpeg', 'png'), f'{url} does not have a valid image type ({file_type})'

	file_name = ""
	if in_cache is None:
		file_name = str(uuid.uuid1()) + '.' + file_type
	else:
		file_name = in_cache
	
	with open('cache\\images\\cache_table.csv', 'a') as cache_table_file:
		cache_table_file.write(to_search + ',' + file_name + '\n')

	with open(f'cache\\images\\{file_name}', 'wb') as img_file:
		for chunk in r.iter_content(1024):
			img_file.write(chunk)

	return file_name


	
















	# ret = ""
	# try:
	# 	# try and get the file from the cache if it exists
	# 	f = open(f"cache\\images\\{file_san(url)}.html", "r", encoding='utf-8')
	# 	print(f"found {file_san(url)} in cache")
	# 	ret = f.read()
	# 	f.close()
	# except:
	# 	continue_flag = False
	# 	tries_left = 5
	# 	while not continue_flag:
	# 		wait_timer(10)
	# 		print("loading up ",url)
	# 		req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	# 		try:
	# 			ret = urllib.request.urlopen(req).read().decode("UTF-8")
	# 			continue_flag = True
	# 		except:
	# 			tries_left -= 1
	# 			print("FAILED TO LOAD:", url)
	# 		if tries_left <= 0:
	# 			raise Exception("ran out of attempts")
				
	# 	f = open(f"cache\\{file_san(url)}.html", "w", encoding='utf-8')
	# 	f.write(ret)
	# 	f.close()

	# print (type (ret))
	# return ret