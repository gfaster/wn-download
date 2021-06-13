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
	

sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations"]














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

		# create the nav file
		out = gen_nav(book)
		with open("tmp/epub/EPUB/nav.xhtml", "w", encoding="utf-8") as file:
			file.write(out)

		# generate package.opf
		out = modify_opf(book)
		with open("tmp/epub/EPUB/package.opf", "w", encoding="utf-8") as file:
			file.write(out) 

		# create the archive
		print("creating archive...")
		archive = ZipFile('tmp/temp.zip', 'w')
		archive.write('epub_template/mimetype', "mimetype")
		zipdir('tmp/epub/META-INF/', archive)
		zipdir('tmp/epub/EPUB/', archive)
		
		archive.close()

		cmd_exec(f'copy /Y tmp\\temp.zip "{location}{book.title}.epub"')





	
	print("Generated volume!")




# def create_volume(start_url, end_url, name):
	

# 	if not DEBUG:
# 		generate(book + "</body>", name, chapter_list, location=f"out/{get_site(start_url)}/", ftype="epub")
# 	else:
# 		generate(book + "</body>", "out", chapter_list, location=f"test/", ftype="epub")


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
		""
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

batch_space = {
	"Galactic-Navy": [
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-1-battleship-iris-conrad-part-1/",
	""
	]
}


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

# The Galactic Navy Officer becomes an Adventurer
galactic_adventurer = Book("The Galactic Navy Officer becomes an Adventurer")
galactic_adventurer.append(Section("Volume 1 – Chance Encounter",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-1-battleship-iris-conrad-part-1/",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-20-gotania-part-2/"))
galactic_adventurer.append(Section("Volume 2 – Adventurer",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-21-adventurers-guild-1-part-1/",
	"https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/chapter-85-rescue-operation-1-part-4/"))

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
	"https://www.wuxiaworld.com/novel/second-life-ranker/slr-chapter-480"
	))




generation_target = slr
if not DEBUG:
	generate(generation_target, location=f"out/{get_site(generation_target.sections[0].first_chapter_url)}/", ftype="epub")
else:
	generation_target.title = "out"
	generate(generation_target, location=f"test/", ftype="epub")
