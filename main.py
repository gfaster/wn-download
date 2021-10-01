import time
import os
import urllib.request
import re
import html
import sys
from bs4 import BeautifulSoup
from src.aux_func import *
from src.sites.wuxiaWorld import *
from src.sites.isekaiLunatic import *
from src.sites.lightnovelstranslations import *
from zipfile import ZipFile
from epubcheck import EpubCheck
import pprint
import shutil
import yaml
from pathlib import Path


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def loadBook(yamlLocation):
    file = open(yamlLocation)
    defintion = yaml.load(file, Loader=yaml.SafeLoader)
    bookDefintion = Book(defintion['title'])
    for section in defintion['sections']:
        bookDefintion.append(Section(
            section['name'],
            section['startUrl'],
            section['endUrl']
        ))
    return bookDefintion


def generate(book: Book, location: Path):
    # make a fresh tmp subfolder
    print("clearing the tmp folder...")
    if not Path("tmp").is_dir():
       Path("tmp").mkdir()
    if not Path("tmp/epub"):
       Path("tmp/epub").mkdir()
    if Path("tmp/epub/EPUB").is_dir():
    	shutil.rmtree(Path("tmp/epub/EPUB"))
    if Path("tmp/epub/META-INF").is_dir():
    	shutil.rmtree(Path("tmp/epub/META-INF"))
    


    # copy over constant materialsloadBook
    print("copying template materials...")
    copytree('epub_template/const_files/', 'tmp/epub/') 
    # create the main file
    print("creating the core files...")
    for section in book:
        print(f"tmp/epub/EPUB/{section.file_title}.xhtml")
        sectionPath = Path(f"tmp/epub/EPUB/{section.file_title}.xhtml")
        with open(sectionPath, "w", encoding="utf-8") as file:
            file.write(section.generate_html())
    # copying images
    for image in book.get_images():
        print(image)
        shutil.copy(Path(f"cache/images/{image}"), Path("tmp/epub/EPUB/images/"))
    # create the nav file
    out = gen_nav(book)
    with open(Path("tmp/epub/EPUB/nav.xhtml"), "w", encoding="utf-8") as file:
        file.write(out)

    # generate package.opf and toc.ncx
    out = modify_opf(book)
    with open(Path("tmp/epub/EPUB/package.opf"), "w", encoding="utf-8") as file:
        file.write(out)

    out = modify_ncx(book)
    with open(Path("tmp/epub/EPUB/toc.ncx"), "w", encoding="utf-8") as file:
        file.write(out)

    # create the archive
    print("creating archive...")
    archive = ZipFile('tmp/temp.zip', 'w')
    archive.write('epub_template/mimetype', "mimetype")
    zipdir(Path('tmp/epub/META-INF/'), archive)
    zipdir(Path('tmp/epub/EPUB/'), archive)

    archive.close()
    shutil.copy2(Path('tmp/temp.zip'),location / f"{book.title}.epub")

    result = EpubCheck(location / f"{book.title}.epub")
    if not result.valid:
        print("FINAL EPUB IS INVALID")
        if DEBUG or True:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(result.messages)

    print("Generated volume!")


generation_target = loadBook(sys.argv[1])
if not DEBUG:
    generate(generation_target,
             location=Path("out/"))
else:
    # print([section.first_chapter_url for section in generation_target])
    generation_target.title = "Debug Book"
    generate(generation_target, location=Path("test/"))
