import time
import os
import urllib.request
import re
import html
import sys
from bs4 import BeautifulSoup
from aux_func import *
from sites.wuxiaWorld import *
from sites.isekaiLunatic import *
from sites.lightnovelstranslations import *
	

sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations"]

DEBUG = True













def generate(body_html, title, ftype="pdf", location="out/"):
	
	
	

	if ftype == "pdf":
		out = "<!DOCTYPE html> <html lang=\"en\">\n <head><meta charset=\"UTF-8\"><title>Book</title></head>\n\n"
		tmp = body_html
		out += "</html>"
		with open(f"tmp/{title}.html", "w", encoding="utf-8") as file:
			file.write(out)
		cmd = f"wkhtmltopdf --user-style-sheet stylesheet.css \"tmp/{title}.html\" \"{location}{title}.pdf\" "
		cmd_exec(cmd)
	if ftype == "epub":
		out = """<?xml version="1.0" encoding="UTF-8"?>
				<!DOCTYPE html>
				<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en"
					xml:lang="en" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/#">
					<head>
						<title>Book</title>
						<link href="css/epub.css" type="text/css" rel="stylesheet" />
					</head>"""
		tmp = body_html
		out += "</html>"

		# copy over template materials
		cmd_exec("rmdir tmp\\template_1")
		cmd_exec("xcopy /E epub_template\\template_1 tmp\\")
		with open(f"tmp/template_1/so4.xhtml", "w", encoding="utf-8") as file:
			file.write(out)

		# this is beyond disgusting, I hate it
		# need to figure out a dataclass for this so I don't have to pass chapters
		out = gen_nav("Book", list(range(200)), list(range(200)))
		with open(f"tmp/template_1/nav.xhtml", "w", encoding="utf-8") as file:
			file.write(out)

	# HTML(string=out).write_pdf( f"{title}.pdf")
	
	print("Generated File!")

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

def gen_nav(title, chapters:list, chapternums:list):
	header = """ <?xml version="1.0" encoding="utf-8"?>
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
	<ol id="tocList">
	""".format(title)

	footer = """
	</ol>
	</nav>
	</body>
	</html>
	"""

	line = """ 
	<li>
		<a href="s04.xhtml#chapter-{}">
			{}
		</a>
	</li>
	"""

	out = header

	for chap, num in zip(chapters, chapternums):
		assert isinstance(num, (int, float))
		out += line.format(num, chap)
	out += footer

	return out

def gen_ncx(title, chapters:list, chapternums:list):
	pass
	# this would only be used for backward compatibility (ewwww)

def create_volume(start_url, end_url, name):
	url = start_url
	book = "<body>"
	count = 1
	max_count = 5000
	parser_type = get_parser(url)
	if DEBUG:
		max_count = 5

	while url is not None and count <= max_count and url != end_url:
		parser = parser_type(load_site(url=url), count)

		url = parser.get_next_cptr_url()

		book += f"<div id=\"chapter-{count}\">"
		book += parser.get_content()
		book += "</div>"
		
		count += 1

	if not DEBUG:
		generate(book + "</body>", name, location=f"out/{get_site(start_url)}/")
	else:
		generate(book + "</body>", "out", location=f"test/")


batcht= {
	"Tsuki-Tome-1": [
		"https://isekailunatic.wordpress.com/2015/09/19/prologue-this-is-the-beginning-of-the-autumn-sky/",
		"https://isekailunatic.wordpress.com/2016/01/01/chapter-66-looking-at-the-departing-back/"
	],
	"Tsuki-Tome-2": [
		"https://isekailunatic.wordpress.com/2016/01/01/chapter-66-looking-at-the-departing-back/",
		"https://isekailunatic.wordpress.com/2016/05/14/chapter-111-school-festival-is-soon-to-come/"
	],
	"Tsuki-Tome-3": [
		"https://isekailunatic.wordpress.com/2016/05/14/chapter-111-school-festival-is-soon-to-come/",
		"https://isekailunatic.wordpress.com/2019/04/30/chapter-172-fair-weather-girlfriend/"
	],
	"Tsuki-Tome-4": [
		"https://isekailunatic.wordpress.com/2019/04/30/chapter-172-fair-weather-girlfriend/",
		"https://isekailunatic.wordpress.com/2017/04/21/chapter-232-everyday-life-and-the-towns-state/"
	],
	"Tsuki-Tome-5": [
		"https://isekailunatic.wordpress.com/2017/04/21/chapter-232-everyday-life-and-the-towns-state/",
		"https://isekailunatic.com/2020/05/31/tsuki-chapter-309-the-identity-of-the-revolutions-antitheism/"
	],
	"Tsuki-Tome-6-2021-05-014": [
		"https://isekailunatic.com/2020/05/31/tsuki-chapter-309-the-identity-of-the-revolutions-antitheism/",
		"https://isekailunatic.com/2021/03/26/tsuki-chapter-394-unexpected-audience-%e2%91%a0/"
	],
	"Tsuki-full": [
		"https://isekailunatic.wordpress.com/2015/09/19/prologue-this-is-the-beginning-of-the-autumn-sky/",
		"https://isekailunatic.com/2021/03/26/tsuki-chapter-394-unexpected-audience-%e2%91%a0/"
	]

	
}

tsuki_full = {
	"Tsuki-full": [
		"https://isekailunatic.wordpress.com/2015/09/19/prologue-this-is-the-beginning-of-the-autumn-sky/",
		" "
	]
}

batch = {
	"slr-volume-1": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-1",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-26"
	],
	"slr-volume-2": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-26",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-51"
	],
	"slr-volume-3": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-51",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-76"
	],
	"slr-volume-4": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-76",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-101"
	],
	"slr-volume-5": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-101",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-126"
	],
	"slr-volume-6": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-126",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-151"
	],
	"slr-volume-7": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-151",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-176"
	],
	"slr-volume-8": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-176",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-201"
	],
	"slr-volume-9": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-201",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-226"
	],
	"slr-volume-10": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-226",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-251"
	],
	"slr-volume-11": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-251",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-276"
	],
	"slr-volume-12": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-276",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-301"
	],
	"slr-volume-13": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-301",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-326"
	],
	"slr-volume-14": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-326",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-351"
	],
	"slr-volume-15": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-351",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-376"
	],
	"slr-volume-16": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-376",
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-401"
	],
	"slr-volume-17": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-401",
		""
	],
	"slr-all": [
		"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-1",
		""
	]

}

batchs = {
	"Stealth-volume-1": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-01-an-invitation-to-another-world/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-22/"
	],
	"Stealth-volume-2": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-22/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-56/"
	],
	"Stealth-volume-3": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-56/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-117/"
	],
	"Stealth-volume-4": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-117/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-178/"
	],
	"Stealth-volume-5": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-178/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-217/"
	],
	"Stealth-Akira-Aida": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-217/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-240/"
	],
	"Stealth-Volume-6": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-240/",
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-286-teaser/"
	],
	"Stealth-All": [
		"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-01-an-invitation-to-another-world/",
		""
	]

}

batchk = {
	"Arrow-knee-vol-1": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-1/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-42/"
	],
	"Arrow-knee-vol-2": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-42/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-81/"
	],
	"Arrow-knee-vol-3": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-81/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-114/"
	],
	"Arrow-knee-vol-4": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-114/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-139/"
	],
	"Arrow-knee-vol-5": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-139/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-173/"
	],
	"Arrow-knee-vol-6": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-173/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-216/"
	],
	"Arrow-knee-vol-7": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-216/",
	"https://lightnovelstranslations.com/the-strongest-wizard/57746-2/"
	],
	"Arrow-knee-vol-8": [
	"https://lightnovelstranslations.com/the-strongest-wizard/57746-2/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-300/"
	],
	"Arrow-knee-vol-9": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-300/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-349/"
	],
	"Arrow-knee-vol-10": [
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-349/",
	"https://lightnovelstranslations.com/the-strongest-wizard/chapter-394/"
	],
}

batchdf = {
	"dragon-friend-vol-1": [
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/chapter-1-dragon-san-is-a-loner/",
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-34/"
	],
	"dragon-friend-vol-2": [
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-34/",
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-68/"
	],
	"dragon-friend-vol-3": [
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-68/",
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-102/"
	],
	"dragon-friend-vol-4": [
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-102/",
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-152/"
	],
	"dragon-friend-vol-5": [
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-152/",
		"https://lightnovelstranslations.com/dragon-san-wants-a-friend/dragon-san-wants-a-friend-chapter-185/"
	],
}

batchwm = {
	"wm-full": [
	"https://isekailunatic.com/2020/02/12/wm-prologue-1-a-class-stranded/",
	""
	]
}

batch_to_gen = tsuki_full

for volume in batch_to_gen:
	create_volume(batch_to_gen[volume][0], batch_to_gen[volume][1], volume)