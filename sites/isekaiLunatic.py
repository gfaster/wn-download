import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from html.parser import HTMLParser
import re
import html

DEBUG = False

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
		if tag in ("script","figure"):
			self.bad_tag = True

		if self.content and tag in ("p", "i", "b", "em", "br", "strong"):
			self.out += f"<{tag}>"

		if ("class","entry-content") in attrs:
			self.content = True
			# print("content start")

		if tag == "title":
			self.istitle = True

		if self.content and tag == "a":
			# print("found link")
			self.islink=True
			self.link_store = [v for i, v in enumerate(attrs) if v[0] == "href"][0][1]

		if self.content and tag == "hr":
			self.out += "\n<hr>\n"



	def handle_endtag(self, tag):
		if tag in ("script","figure"):
			assert self.bad_tag
			self.bad_tag = False


		if self.content and tag == "div" and not self.bad_tag:
			# assert "Next Chapter" in self.out or "Previous Chapter" in self.out or "Next chapter" in self.out or "Previous chapter" in self.out
			assert self.next_cptr_url or self.prev_cptr_url
			self.content = False

		if self.content and tag in ("i", "b", "em", "br", "strong"):
			self.out += f"</{tag}>"

		if self.content and tag == "p":
			self.out += "</p>\n\n"

		if self.islink:
			self.islink = False

		if self.istitle:
			self.istitle = False



	def handle_data(self, data):
		if self.content and not self.bad_tag and not self.islink:
			new_l = san(data)
			self.out += new_l if " l "  not in new_l else ""

		if self.islink:
			self.islink = False
			assert self.link_store
			if "Previous Chapter" in data or "Previous chapter" in data:
				# print(f"found prev: {self.link_store}")
				self.prev_cptr_url = self.link_store
				self.link_store = None
			elif "Next Chapter" in data or "Next chapter" in data:
				# print(f"found next: {self.link_store}")
				self.next_cptr_url = self.link_store
				self.link_store = None
			else:
				# print(f"weird link found [{data}]({self.link_store})")
				self.out += f"<a href=\"{san(self.link_store)}\">{data}</a>"
				self.link_store = None

		if self.istitle:
			tsplit = data.split(" – ")
			if "Tsuki" in tsplit[0] or "WM" in tsplit[0]:
				self.cptr_title = tsplit[1:-1]
			else:
				self.cptr_title = tsplit[0:-1]
			self.cptr_title = san(' – '.join(self.cptr_title))





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
		return self.out.replace(r"<p> l </p>", " ")
		# return re.sub(r"<p>l<\/p>", " ", san(self.out))
