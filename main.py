from html.parser import HTMLParser
import time
import os
import urllib.request
import re
import html
	
from pathvalidate import sanitize_filename
sites = ["WuxiaWorld", "IsekaiLunatic"]

DEBUG = False

def generate(body_html, title, ftype="pdf"):
	
	out = "<!DOCTYPE html> <html lang=\"en\">\n <head><meta charset=\"UTF-8\"><title>Book</title></head>\n\n"
	tmp = body_html
	out += re.sub(r'(Next Chapter)|(Previous Chapter)', '', tmp)
	out += "</html>"
	

	if ftype == "pdf":
		with open(f"tmp/{title}.html", "w", encoding="utf-8") as file:
			file.write(out)
		os.system(f"wkhtmltopdf --user-style-sheet stylesheet.css \"tmp/{title}.html\" \"{title}.pdf\" ")
	if ftype == "epub":
		with open(f"tmp/{title}.html", "w", encoding="utf-8") as file:
			file.write(out)

	# HTML(string=out).write_pdf( f"{title}.pdf")
	
	print("Generated File!")

def file_san(string):
	out = sanitize_filename(string)
	return out.replace(r".", "_")

def load_site(url=""):
	if DEBUG:
		f = open("test\\WM – Prologue_ 1-A Class Stranded – Reigokai_ Isekai Translations.html", "r", encoding='utf-8')
		out = f.read()
		f.close()
		# print(out)
		# return out.decode("utf-8")
	# raise Exception("NOT IMPLEMENTED")
	ret = ""
	try:
		f = open(f"cache\\{file_san(url)}.html", "r", encoding='utf-8')
		print(f"found {file_san(url)} in cache")
		ret = f.read()
		f.close()
	except:
		print("waiting...", end="\r")
		time.sleep(10)
		print("loading up ",url)
		req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		ret = urllib.request.urlopen(req).read().decode("UTF-8")
		f = open(f"cache\\{file_san(url)}.html", "w", encoding='utf-8')
		f.write(ret)
		f.close()

	# print (type (ret))
	return ret.replace(r"&nbsp;", " ")


def san(string):
	no_q = html.escape(string).replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c","\"").replace(u"\u201d", "\"")
	# return re.sub(r'(?=[^\w\-_\. \[\]\(\)\?\<\>…\/,\%\$\#\!\~])(?=^"\n")', ' ',no_q)
	# return html.escape(html.unescape(string))
	# return string
	return no_q




class WuxiaWorld(HTMLParser):
	def __init__(self, convert_charrefs=True):
		super().__init__(convert_charrefs=convert_charrefs)
		self.bad_tag = False
		self.content = False
		self.out = ""
		self.rawdata = ""
		self.link_store = None
		self.next_cptr_url = None
		self.prev_cptr_url = None
		self.islink = False
		self.cptr_title = ""
		self.istitle = False
		self.isitalicstyle = False
		


	def handle_starttag(self, tag, attrs):
		if tag == "script":
			self.bad_tag = True

		if self.content and tag in ("p", "i", "b", "em", "br", "strong"):
			self.out += f"<{tag}>"

		if self.content and tag == "span":
			style_tag = [v for i, v in enumerate(attrs) if v[0] == "style"][0][1]
			if re.search(r"font-style: ?italic", style_tag):
				self.out += "<em>"
				self.isitalicstyle = True


		if ("id","chapter-content") in attrs:
			self.content = True
			# print("content start")

		if tag == "title":
			self.istitle = True

		if self.content and ("class", "chapter-nav") in attrs:
			self.islink=True
			self.link_store = [v for i, v in enumerate(attrs) if v[0] == "href"][0][1]



	def handle_endtag(self, tag):
		if tag == "script":
			assert self.bad_tag
			self.bad_tag = False


		if self.content and tag == "div":
			assert "Next Chapter" in self.out or "Previous Chapter" in self.out
			self.content = False

		if self.content and tag in ("p", "i", "b", "em", "strong"):
			self.out += f"</{tag}>"
			if tag == "p":
				self.out += "\n\n"

		if self.isitalicstyle and tag == "span":
			self.out += "</em>"
			self.isitalicstyle = False


		if self.islink:
			self.islink = False

		if self.istitle:
			self.istitle = False



	def handle_data(self, data):
		if self.content and not self.bad_tag:
			self.out += san(data)

		if self.islink:
			self.islink = False
			assert self.link_store
			if "Previous" in data:
				# print(f"found prev: {self.link_store}")
				self.prev_cptr_url = self.link_store
				self.link_store = None
			elif "Next" in data:
				# print(f"found next: {self.link_store}")
				self.next_cptr_url = self.link_store
				self.link_store = None
			else:
				print(f"weird link found [{data}]({self.link_store})")
				self.link_store = None

		# generates title - needs to acocunt for different styles
		if self.istitle:
			# self.cptr_title = data.split(" - ")[1:3]
			# if len(data.split(" - ")) < 4:
			self.cptr_title = re.split(r"( - )|(\. )", data)[3:-3:3]
			self.cptr_title = ' - '.join(self.cptr_title)




	def get_next_cptr_url(self):
		n = ("https://www.wuxiaworld.com" if "http" not in self.next_cptr_url else "") + self.next_cptr_url
		if self.next_cptr_url and not DEBUG:
			return n
		if self.next_cptr_url:
			print(f"next chapter would be {n}")
			return None
		print("No next chapter found")
		return None

	def get_out(self):
		return self.out

class IsekaiLunatic(HTMLParser):
	def __init__(self, convert_charrefs=True):
		super().__init__(convert_charrefs=convert_charrefs)
		self.bad_tag = False
		self.content = False
		self.out = ""
		self.rawdata = ""
		self.link_store = None
		self.next_cptr_url = None
		self.prev_cptr_url = None
		self.islink = False
		self.cptr_title = ""
		self.istitle = False
		


	def handle_starttag(self, tag, attrs):
		if tag == "script":
			self.bad_tag = True

		if self.content and tag == "p":
			self.out += "\n<p>"

		if ("class","entry-content") in attrs:
			self.content = True
			# print("content start")

		if ("class", "entry-title") in attrs:
			self.istitle = True

		if self.content and tag == "a":
			# print("found link")
			self.islink=True
			self.link_store = [v for i, v in enumerate(attrs) if v[0] == "href"][0][1]

		if self.content and tag == "hr":
			self.out += "\n<hr>\n"



	def handle_endtag(self, tag):
		if tag == "script":
			assert self.bad_tag
			self.bad_tag = False


		if self.content and tag == "div":
			assert "Next Chapter" in self.out or "Previous Chapter" in self.out
			self.content = False

		if self.content and tag == "p":
			self.out += "</p>\n\n"

		if self.islink:
			self.islink = False

		if self.istitle:
			self.istitle = False



	def handle_data(self, data):
		if self.content and not self.bad_tag:
			new_l = san(data).replace("<", r"&lt;")
			self.out += new_l if new_l != "l" else ""

		if self.islink:
			self.islink = False
			assert self.link_store
			if "Previous Chapter" in data:
				# print(f"found prev: {self.link_store}")
				self.prev_cptr_url = self.link_store
				self.link_store = None
			elif "Next Chapter" in data:
				# print(f"found next: {self.link_store}")
				self.next_cptr_url = self.link_store
				self.link_store = None
			else:
				print(f"weird link found [{data}]({self.link_store})")
				self.link_store = None

		if self.istitle:
			self.cptr_title = data.split(" – ")[1:]
			self.cptr_title = san(' - '.join(self.cptr_title))





	def get_next_cptr_url(self):
		if not self.next_cptr_url: return None
		n = ("https://www.isekailunatic.com" if "http" not in self.next_cptr_url else "") + self.next_cptr_url
		if self.next_cptr_url and not DEBUG:
			return n
		if self.next_cptr_url:
			print(f"next chapter would be {n}")
			return None
		print("No next chapter found")
		return None

	def get_out(self):
		return san(self.out).replace(r"<p>l</p>", " ")
		# return re.sub(r"<p>l<\/p>", " ", san(self.out))

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
	"Tsuki-Tome-6-2021-03-05": [
		"https://isekailunatic.com/2020/05/31/tsuki-chapter-309-the-identity-of-the-revolutions-antitheism/",
		"https://isekailunatic.com/2021/03/01/tsuki-chapter-388-unequivalent-exchange/"
	],
	
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
}




for volume in batch:
	hasnext = True
	url = batch[volume][0]
	end_url = batch[volume][1]
	book = "<body>"
	count = 1
	while hasnext and count <= 100 and url != end_url:
		parser = WuxiaWorld()
		parser.feed(load_site(url=url))

		book += "<div>"
		book += "<div class=\"new-chapter\">"
		book += "<h2>" + parser.cptr_title + "</h2>"
		book += "</div>"


		url = parser.get_next_cptr_url()
		book += parser.get_out().replace("<p>l<\\/p>", "")
		# assert "<p>l<\\/p>" not in book
		book += "</div>"
		print("finished chapter ", parser.cptr_title)
		hasnext = url is not None
		if url == end_url: break
		count += 1

	generate(book + "</body>", volume)