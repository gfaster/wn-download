import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aux_func import *
from html.parser import HTMLParser
import re
import html

DEBUG = False

class LightNovelsTranslations(HTMLParser):
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
		self.div_nest = 0
		self.found_next = False
		self.is_last = False

		# after the start, lnt chapters follow the following pattern:
		# <hr> <p> [Translator] </p> <hr> <p> [title (without ch #)] </p>
		# TODO: skip with countdown
		self.start_countdown = 2
		


	def handle_starttag(self, tag, attrs):

		if tag in ("script","figure"):
			self.bad_tag = True

		if ("class","alignright") in attrs and self.content and self.start_countdown == 2:
			# print("found next!!!")
			self.found_next = True

		if tag == "title":
			self.istitle = True

		if ("class","entry-content") in attrs:
			self.content = True
			# print("content start")

		if (self.content and tag == "a" and self.div_nest == 2) or (self.found_next and tag == "a") and not self.is_last and self.found_next:
			# print("found link")
			self.islink=True
			self.link_store = [v for i, v in enumerate(attrs) if v[0] == "href"][0][1]
			assert self.link_store
			self.found_next = False

		if tag == "div" and self.content:
			self.div_nest += 1


		# ---------------------------------

		if self.content and self.start_countdown > 0:
			if tag == "hr":
				self.start_countdown -= 1
			# print(f"retyursxcdf {tag}")
			return

		
		# print(self.div_nest)
		if self.content and tag in ("p", "i", "b", "em", "br", "strong") and self.div_nest == 1:
			self.out += f"<{tag}>"
			if tag == "p":
				self.out += " "

		

		
			# print(f"{tag}: {attrs}\t\t {self.div_nest}")
			

		

		

		

		if self.content and tag == "hr":
			self.found_next = False





	def handle_endtag(self, tag):
		if tag in ("script","figure"):
			assert self.bad_tag
			self.bad_tag = False


		if self.content and tag == "div":
			self.div_nest -= 1
			# assert "Next Chapter" in self.out or "Previous Chapter" in self.out or "Next chapter" in self.out or "Previous chapter" in self.out
			if self.div_nest == 0:
				assert self.next_cptr_url or self.prev_cptr_url
				self.content = False

		if self.islink:
			self.islink = False

		if self.istitle:
			self.istitle = False

		# --------------------------------

		if self.content and self.start_countdown > 0:
			return

		if self.content and tag in ("i", "b", "em", "strong") and self.div_nest == 1:
			self.out += f"</{tag}>"

		if self.content and tag == "p" and self.div_nest == 1:
			self.out += "</p>\n\n"

		



	def handle_data(self, data):
		if self.istitle:
			self.cptr_title = data
			if "TEASER" in data:
				self.is_last = True

		if self.islink:
			self.islink = False
			assert self.link_store
			# if "Previous Chapter" in data or "Previous chapter" in data:
			# 	# print(f"found prev: {self.link_store}")
			# 	self.prev_cptr_url = self.link_store
			# 	self.link_store = None
			# if "chapter" in data.casefold() and " - " in data and self.found_next:
			if self.found_next:
				# print(f"found next: {self.link_store}")
				self.next_cptr_url = self.link_store
				self.link_store = None
				self.found_next = False
			else:
				# print(f"weird link found [{data}]({self.link_store})")
				# self.out += f"<a href=\"{san(self.link_store)}\">{data}</a>"

				# Lets just not do links
				self.link_store = None
			if self.found_next:
				raise Exception("messed up next chapter identification")

		if self.content and self.start_countdown > 0:
			return

		# ----------------------------------------

		if self.content and not self.bad_tag and not self.islink and self.div_nest == 1:
			if data.strip() in self.cptr_title: return
			new_l = re.sub(r"\u3011([^ ])",r"】 \1",san(data))
			self.out += new_l

		





	def get_next_cptr_url(self):
		if not self.next_cptr_url: return None
		n = ("https://lightnovelstranslations.com" if "http" not in self.next_cptr_url else "") + self.next_cptr_url
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
