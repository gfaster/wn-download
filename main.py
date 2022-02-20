import time
import os
import urllib.request
import re
import html
import sys
from bs4 import BeautifulSoup
from src.aux_func import *
from src.entities.Book import Book
from src.entities.Section import Section
from src.entities.UrlRange import UrlRange, UrlRangeSet
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
    file = open(yamlLocation, 'r', encoding='utf8')
    definition = yaml.load(file, Loader=yaml.SafeLoader)
    bookDefinition = Book(definition['title'])
    lang = definition['lang'] if ('lang' in definition) else 'en'

    if 'picture' in definition and definition['picture']:
        bookDefinition.set_cover_image(Path(definition['picture']))


    for section in definition['sections']:
        # builds the start and end url pairs
        if 'subsections' in section:
            ur_set = UrlRangeSet(tuple( [UrlRange(sub_sect['startUrl'], sub_sect['endUrl']) for sub_sect in section['subsections']] ))
        else:
            # assert type(section) is dict, f'{type(section) = }'
            ur_set = UrlRangeSet( (UrlRange(section['startUrl'], section['endUrl']),) )

        bookDefinition.append(Section(
            section['name'],
            ur_set,
            lang
        ))
    return bookDefinition


def generate(book: Book, location: Path):
    # make a fresh tmp subfolder
    print("clearing the tmp folder...")
    if not Path("tmp").is_dir():
       Path("tmp").mkdir()
    if not Path("tmp/epub").is_dir():
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
        print(f"-- New Section -- tmp/epub/EPUB/{section.file_title}.xhtml")
        sectionPath = Path(f"tmp/epub/EPUB/{section.file_title}.xhtml")
        with open(sectionPath, "w", encoding="utf-8") as file:
            file.write(section.generate_html())
    # copying images
    for image in book.get_images():
        shutil.copy(Path(f"cache/images/{image}"), Path("tmp/epub/EPUB/images/"))
    cover = book.get_cover_image()
    if cover:
        assert cover.suffix in ('.jpeg', '.jpg', '.png'), f"{cover.name} is not valid image type"
        shutil.copy(book.get_cover_image(), Path(f"tmp/epub/EPUB/images/cover{cover.suffix}"))


    # create the nav file
    out = book.gen_nav()
    with open(Path("tmp/epub/EPUB/nav.xhtml"), "w", encoding="utf-8") as file:
        file.write(out)

    # generate package.opf 
    out = book.modify_opf()
    with open(Path("tmp/epub/EPUB/package.opf"), "w", encoding="utf-8") as file:
        file.write(out)

    #generate toc.ncx
    out = book.modify_ncx()
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

def main():
    generation_target = loadBook(sys.argv[1])
    if not DEBUG:
        generate(generation_target,
                 location=Path("out/"))
    else:
        # print([section.first_chapter_url for section in generation_target])
        generation_target.title = "Debug Book"
        generate(generation_target, location=Path("test/"))

def main_perf():
    assert PERF_TEST
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        main()

    print('\n --- STATS ---')
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()
    stats.dump_stats(filename='test/stats.prof')


if __name__ == '__main__':
    if PERF_TEST:
        main_perf()
    else:
        main()
        