from os import path
from pathlib import Path
from bs4 import BeautifulSoup
from src.Sanitizer import file_san, hyper_san
from src.entities.Section import Section

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
		
	def gen_nav(self):
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
		""".format(self.title)
		# <ol id="tocList">
		# </ol>

		soup = BeautifulSoup(header,features="lxml")

		section_list = soup.new_tag("ol")
		soup.nav.append(section_list)
		for section in self:
			section_li = soup.new_tag("li")
			section_ol = soup.new_tag("ol", id=f"{section.file_title}List")


			last_chap = None
			first_chap = None
			for chapter in section.chapter_list:
				line = soup.new_tag("li")
				line.append(soup.new_tag("a", href=f"{section.file_title}.xhtml#{chapter.ghash()}"))
				line.a.string = chapter.title
				section_ol.append(line)
				last_chap = chapter
				if first_chap is None:
					first_chap = chapter

			section_h2 = soup.new_tag("a", href=f"{section.file_title}.xhtml#{first_chap.ghash()}")
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

	def modify_ncx(self):
		soup = None
		with open(Path('epub_template/dynamic_files/toc.ncx'), 'r') as ncx:
			soup = BeautifulSoup(ncx.read(), "xml")

		soup.docTitle.find('text').string = self.title

		playorder_index = 1
		for section in self:
			sec_navpoint = soup.new_tag('navPoint', attrs={'class':'section', 'id':section.file_title, 'playOrder':str	(playorder_index)})
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
	def modify_opf(self):
		soup = None
		with open(Path('epub_template/dynamic_files/package.opf'), 'r') as opf:
			soup = BeautifulSoup(opf.read(), "xml")
	
		main_title = soup.find('dc:title', id='t1')
		main_title.string = self.title
	
		sub_title = soup.find('dc:title', id='t2')
		sub_title.string = self.title.strip() + " Created with WN-Download"
	
		# <item href="s04.xhtml" id="s04" media-type="application/xhtml+xml"/>
		# <itemref idref="s04"/>
		# add sections files
		for section in self:
			new_tag = soup.new_tag("item", attrs={'href':f"{section.file_title}.xhtml", 'id':section.file_title, 	'media-type': 'application/xhtml+xml'})
			soup.manifest.append(new_tag)
	
			new_tag = soup.new_tag("itemref", idref=section.file_title)
			soup.spine.append(new_tag)
	
		for image in self.get_images():
			assert isinstance(image, str)
			img_type = image.split('.')[-1]
	
			new_tag = soup.new_tag("item", attrs={'href':f"images/{image}", 'id':hyper_san(image), 'media-type': f'image/{img_type}'})
			soup.manifest.append(new_tag)
	
	
		return soup.prettify()	