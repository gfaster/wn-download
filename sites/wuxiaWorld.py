import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from html.parser import HTMLParser
import re
import html

DEBUG = False

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
