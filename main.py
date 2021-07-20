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
from zipfile import ZipFile
from epubcheck import EpubCheck
import pprint
import shutil
	

sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations", "Skythewood"]














def generate(book:Book, ftype="epub", location="out/"):
	
	
	

	# if ftype == "pdf":
	# 	out = "<!DOCTYPE html> <html lang=\"en\">\n <head><meta charset=\"UTF-8\"><title>Book</title></head>\n\n"
	# 	out += body_html
	# 	out += "</html>"
	# 	with open(f"tmp/{title}.html", "w", encoding="utf-8") as file:
	# 		file.write(out)
	# 	cmd = f"wkhtmltopdf --user-style-sheet stylesheet.css \"tmp/{title}.html\" \"{location}{title}.pdf\" "
	# 	cmd_exec(cmd)


	if ftype == "epub":
		

		# make a fresh tmp subfolder
		print("clearing the tmp folder...")
		cmd_exec("rmdir tmp\\epub /s /q")
		cmd_exec("del tmp\\* /q")
		cmd_exec("mkdir tmp\\epub")

		# copy over constant materials
		print("copying template materials...")
		cmd_exec("xcopy /E epub_template\\const_files\\ tmp\\epub\\")

		# create the main file
		print("creating the core files...")
		for section in book:
			with open(f"tmp/epub/EPUB/{section.file_title}.xhtml", "w", encoding="utf-8") as file:
				file.write(section.generate_html())

		# copying images
		for image in book.get_images():
			# print(f'\tImage: {image}')

			# cmd_exec(f'copy "cache/images/{image}" tmp/epub/EPUB/images/')
			shutil.copy(f"cache/images/{image}", 'tmp/epub/EPUB/images/')

		# create the nav file
		out = gen_nav(book)
		# cmd_exec('mkdir tmp/epub/EPUB/images/')
		with open("tmp/epub/EPUB/nav.xhtml", "w", encoding="utf-8") as file:
			file.write(out)

		# generate package.opf and toc.ncx
		out = modify_opf(book)
		with open("tmp/epub/EPUB/package.opf", "w", encoding="utf-8") as file:
			file.write(out) 

		out = modify_ncx(book)
		with open("tmp/epub/EPUB/toc.ncx", "w", encoding="utf-8") as file:
			file.write(out) 

		# create the archive
		print("creating archive...")
		archive = ZipFile('tmp/temp.zip', 'w')
		archive.write('epub_template/mimetype', "mimetype")
		zipdir('tmp/epub/META-INF/', archive)
		zipdir('tmp/epub/EPUB/', archive)
		
		archive.close()

		cmd_exec(f'copy /Y tmp\\temp.zip "{location}{book.title}.epub"')

		result = EpubCheck(f"{location}{book.title}.epub")
		if not result.valid:
			print("FINAL EPUB IS INVALID")
			if DEBUG or True:
				pp = pprint.PrettyPrinter(indent=4)
				pp.pprint(result.messages)






	
	print("Generated volume!")




# weakest mage
weakestmage = Book("Clearing an Isekai with the Zero-Believers Goddess – The Weakest Mage among the Classmates")
weakestmage.append(Section("1st Arc: First Time in a Parallel World", 
	"https://isekailunatic.wordpress.com/2020/02/12/wm-prologue-1-a-class-stranded/",
	"https://isekailunatic.wordpress.com/2020/03/07/wm-chapter-25-epilogue/"
	))
weakestmage.append(Section("2nd Arc: Laberintos", 
	"https://isekailunatic.wordpress.com/2020/03/09/wm-chapter-26-27-takatsuki-makoto-is-at-his-stagnation-phase/",
	"https://isekailunatic.com/2020/04/12/wm-chapter-57-58-takatsuki-makoto-speaks-to-princess-sofia-epilogue/"
	))
weakestmage.append(Section("3rd Arc: Water Country Capital", 
	"https://isekailunatic.com/2020/04/29/wm-chapter-59-sasaki-aya-is-guided-in-the-city-of-makkaren/",
	"https://isekailunatic.com/2020/05/25/wm-chapter-76-epilogue-third-arc/"
	))
weakestmage.append(Section("4th Arc: Sun Country’s Capital",
	"https://www.isekailunatic.com/2020/05/25/wm-chapter-77-takatsuki-makoto-remembers/",
	"https://www.isekailunatic.com/2020/07/12/wm-chapter-109-epilogue-4th-arc/"
	))
weakestmage.append(Section("5th Arc: Water City of Makkaren",
	"https://www.isekailunatic.com/2020/07/13/wm-chapter-110-takatsuki-makoto-returns-to-the-water-city/",
	"https://www.isekailunatic.com/2020/08/04/wm-chapter-125-epilogue-fifth-arc/"
	))
weakestmage.append(Section("6th Arc: Wood Country and Lucy returning to her homeland",
	"https://www.isekailunatic.com/2020/08/05/wm-chapter-126-takatsuki-makoto-explores/",
	"https://www.isekailunatic.com/2020/09/20/wm-chapter-148-epilogue-sixth-arc/"
	))
weakestmage.append(Section("7th Arc: Fire Country",
	"https://www.isekailunatic.com/2020/09/22/wm-chapter-149-princess-sofia-arrives-at-the-wood-country/",
	"https://www.isekailunatic.com/2020/11/09/wm-chapter-171-7th-arc-epilogue/"
	))
weakestmage.append(Section("8th Arc: War",
	"https://www.isekailunatic.com/2020/11/13/wm-chapter-172-takatsuki-makoto-speaks-to-his-comrades/",
	"https://www.isekailunatic.com/2020/12/28/wm-chapter-197-8th-arc-epilogue/"
	))
weakestmage.append(Section("9th Arc: Farewell ",
	"https://www.isekailunatic.com/2020/12/28/wm-chapter-198-lucys-comrade-wont-just-obediently-stay-hospitalized/",
	"https://www.isekailunatic.com/2021/02/03/wm-chapter-223-epilogue-9th-arc/"
	))
weakestmage.append(Section("10th Arc: 1,000 Years In The Past",
	"https://www.isekailunatic.com/2021/02/05/wm-chapter-224-takatsuki-makoto-arrives-1000-years-into-the-past/",
	"https://www.isekailunatic.com/2021/06/20/wm-chapter-294-takatsuki-makoto-achieves-the-reunion/"
	))



# The Galactic Navy Officer becomes an Adventurer
galactic_adventurer = Book("The Galactic Navy Officer becomes an Adventurer")
galactic_adventurer.append(Section("Volume 1 – Chance Encounter",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-1-battleship-iris-conrad-part-1/",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-20-gotania-part-2/"))
galactic_adventurer.append(Section("Volume 2 – Adventurer",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-21-adventurers-guild-1-part-1/",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-88-royal-capital-search-and-destroy-operation-part-2/"))

# Second Life Ranker
slr = Book("Second Life Ranker")
slr.append(Section("Volume 1", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-1", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-25"
	))
slr.append(Section("Volume 2", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-26", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-50"
	))
slr.append(Section("Volume 3", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-51", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-75"
	))
slr.append(Section("Volume 4", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-76", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-100"
	))
slr.append(Section("Volume 5", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-101", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-125"
	))
slr.append(Section("Volume 6", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-126", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-150"
	))
slr.append(Section("Volume 7", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-151", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-175"
	))
slr.append(Section("Volume 8", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-176", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-200"
	))
slr.append(Section("Volume 9", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-201", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-225"
	))
slr.append(Section("Volume 10", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-226", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-250"
	))
slr.append(Section("Volume 11", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-251", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-275"
	))
slr.append(Section("Volume 12", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-276", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-300"
	))
slr.append(Section("Volume 13", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-301", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-325"
	))
slr.append(Section("Volume 14", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-326", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-350"
	))
slr.append(Section("Volume 15", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-351", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-375"
	))
slr.append(Section("Volume 16", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-376", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-400"
	))
slr.append(Section("Volume 17", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-401", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-425"
	))
slr.append(Section("Volume 18", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-426", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-450"
	))
slr.append(Section("Volume 19", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-451", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-475"
	))
slr.append(Section("Volume 20", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-476", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-500"
	))
slr.append(Section("Volume 21", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-501", 
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-516"
	))

tsukimichi = Book("Tsuki ga Michibiku Isekai Douchuu")
tsukimichi.append(Section("Wandering in the ends of the world Arc", 
	"https://www.isekailunatic.com/2015/09/19/prologue-this-is-the-beginning-of-the-autumn-sky/", 
	"https://www.isekailunatic.com/2015/10/01/chapter-31-gossip-about-the-the-hero-of-gritonia/"
	))
tsukimichi.append(Section("A chapter in the lifestyle of Tsige Arc", 
	"https://www.isekailunatic.com/2015/10/03/chapter-32-the-report-of-the-secretary-ema/", 
	"https://www.isekailunatic.com/2015/12/29/chapter-65-gossip-gritonias-hero-2/"
	))
tsukimichi.append(Section("Second Tome – Chance Meeting in Rotsgard Arc", 
	"https://www.isekailunatic.com/2016/01/01/chapter-66-looking-at-the-departing-back/", 
	"https://www.isekailunatic.com/2016/05/12/chapter-110-summer-vacations-part-2-last-migration-interview/"
	))
tsukimichi.append(Section("Third Tome – Kaleneon’s Participation in War Arc", 
	"https://www.isekailunatic.com/2016/05/14/chapter-111-school-festival-is-soon-to-come/", 
	"https://www.isekailunatic.com/2019/04/30/chapter-171-if-winter-comes/"
	))
tsukimichi.append(Section("Fourth Tome: Kuzunoha’s Tour", 
	"https://www.isekailunatic.com/2019/04/30/chapter-172-fair-weather-girlfriend/", 
	"https://www.isekailunatic.com/2017/04/17/chapter-231-whirling-banquet/"
	))
tsukimichi.append(Section("Fifth Tome: Labyrinth of Lorel", 
	"https://www.isekailunatic.com/2017/04/21/chapter-232-everyday-life-and-the-towns-state/", 
	"https://www.isekailunatic.com/2020/05/27/tsuki-chapter-307-cant-run-away-from-rembrandt/"
	))
tsukimichi.append(Section("Sixth Tome: Setting Sun of Aion", 
	"https://www.isekailunatic.com/2020/05/31/tsuki-chapter-309-the-identity-of-the-revolutions-antitheism/", 
	"https://isekailunatic.com/2021/06/09/tsuki-chapter-415-pillow-talk/"
	))

undetectable = Book("The Undetectable Strongest Job: Rule Breaker")
undetectable.append(Section("Volume 1: 「Concealed」 In another world using the Skill Tree",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-01-an-invitation-to-another-world/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-21/"
	))
undetectable.append(Section("Volume 2: Adventurer Hikaru",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-22/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-55/"
	))
undetectable.append(Section("Volume 3: Academic City and Sun Halo Sorcerer",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-56/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-116/"
	))
undetectable.append(Section("Volume 4: Kingdom Dance",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-117/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-177/"
	))
undetectable.append(Section("Volume 5: Tower of Corruption and Innocent Knight",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-178/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-216/"
	))
undetectable.append(Section("Intermission: Overlapping words, overlapping hearts",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-217/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-239/"
	))
undetectable.append(Section("Volume 6: Spy Wars",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-240/",
	"https://lightnovelstranslations.com/the-undetectable-strongest-job-rule-breaker/chapter-334/"
	))

raisedbydeath = Book("The Girl Raised by the Death God Holds the Sword of Darkness in Her Arms")
raisedbydeath.append(Section("Volume One",
	"http://skythewood.blogspot.com/2019/11/D11.html",
	"http://skythewood.blogspot.com/2019/12/D16.html"
	))
raisedbydeath.append(Section("Volume Two",
	"http://skythewood.blogspot.com/2020/01/D21.html",
	"http://skythewood.blogspot.com/2020/02/D27.html"
	))
raisedbydeath.append(Section("Volume Three",
	"http://skythewood.blogspot.com/2020/02/D30.html",
	"http://skythewood.blogspot.com/2020/04/D37.html"
	))
raisedbydeath.append(Section("Volume Four",
	"http://skythewood.blogspot.com/2020/10/D41.html",
	"http://skythewood.blogspot.com/2020/11/D48.html"
	))



generation_target = slr
if not DEBUG:
	generate(generation_target, location=f"out/{get_site(generation_target.sections[0].first_chapter_url)}/", ftype="epub")
else:
	# print([section.first_chapter_url for section in generation_target])
	generation_target.title = "Debug Book"
	generate(generation_target, location=f"test/", ftype="epub")
