from dataclasses import dataclass, field
from urllib.parse import urlparse
import urllib
from pathlib import Path
from src.Sanitizer import file_san

from src.Sanitizer import *
from src.sites.wuxiaWorld import *
from src.sites.isekaiLunatic import *
from src.sites.lightnovelstranslations import *
from src.sites.skythewood import *
from src.sites.ncode import *
from src.entities.UrlRange import *
from src.aux_func import DEBUG, wait_timer, setup_cache
@dataclass(order=True)
class Section(object):
    title: str
    url_ranges: UrlRangeSet = field(repr=False)
    lang: str = field(default = 'en', repr=False)
    chapter_list: list = field(repr=False, init=False)
    file_title: str = field(init=False)
    images: set = field(init=False, repr=False, hash=False)

    def __post_init__(self):
        self.file_title = '_' + file_san(self.title, self.lang)

        self.chapter_list = list()
        self.images = set()
        assert self.url_ranges.ranges
        for u_range in self.url_ranges.ranges:
            assert u_range.startUrl != "", "no first chapter url"
            assert u_range.endUrl != "", "no final chapter url"

    def get_images(self):
        for chapter in self.chapter_list:
            self.images |= chapter.images
        return self.images

    def generate_html(self) -> str:
        
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
        
        if DEBUG:
        	max_count = 5
        for u_range in self.url_ranges.ranges:
            url = u_range.startUrl
            assert url != "", "start url is blank"
            parser_type = self.get_parser(url)

            while url is not None and count <= max_count:

                parser = parser_type(load_site(url=url), count)
                next_url = parser.get_next_cptr_url()

                chapter = parser.get_content()
                assert len(chapter.content) > 0
                html += f"<section id=\"{chapter.ghash()}\">"
                html += chapter.content
                html += "</section>"

                assert len(html) < 4000000, "Section is too long"

                self.chapter_list.append(chapter)
                if url == u_range.endUrl:
                    break
                url = next_url
                count += 1
        html += "</body></html>"
        # print(html)
        return html

    def get_parser(self, url):
        print(url)
        c_url = get_site(url).casefold()
        c_sites = [x.casefold() for x in sites]
        # print(f"Site is: {c_url}")
        assert c_url in c_sites, "{} is not in the sites list".format(c_url)
        parser_class_name = sites[c_sites.index(c_url)]
        # gets the parser class located in the [site].py
        ret = getattr(sys.modules[__name__], parser_class_name)
        assert issubclass(
            ret, BaseParser), f"{parser_class_name} does not inherit from BaseParser"
        return ret



def load_site(url=""):
    ret = ""
    setup_cache()

    try:
        # try and get the file from the cache if it exists
        f = open(Path(f"cache/pages/{url_to_str_san(url)}.html"),
                 "r", encoding='utf-8')
        print(f"found {url_to_str_san(url)} in cache")
        ret = f.read()
        f.close()
    except FileNotFoundError:
        continue_flag = False
        tries_left = 5
        while not continue_flag:
            wait_timer(10)
            print(f"loading page: {url=!r}")
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0 (epubbot scraper)'})
            try:
                ret = urllib.request.urlopen(req).read().decode("UTF-8")
                continue_flag = True
            except Exception as e:
                tries_left -= 1
                print(f"FAILED TO LOAD: {url}: Error: {e}")
            if tries_left <= 0:
                raise Exception("ran out of attempts")

        f = open(Path(f"cache/pages/{url_to_str_san(url)}.html"),
                 "w", encoding='utf-8')
        f.write(ret)
        f.close()

    # print (type (ret))
    return ret
