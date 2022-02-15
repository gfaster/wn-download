import html
import re
from urllib.parse import urlparse
from pathvalidate import sanitize_filename
from jcconv import kata2hira
import src.aux_func
import base64
from sudachipy import tokenizer
from sudachipy import dictionary


sites = ["WuxiaWorld", "IsekaiLunatic", "LightNovelsTranslations", "Skythewood", "Ncode"]


class JapaneseSan:
	# for converting japanese text to alphanumeric characters
	mode = None
	tokenizer_obj = None
	

	def _setup():
		if JapaneseSan.tokenizer_obj is None:
			JapaneseSan.mode = tokenizer.Tokenizer.SplitMode.C
			JapaneseSan.tokenizer_obj = dictionary.Dictionary().create()

	@staticmethod
	def kana_readings(text, delimiter=''):
		JapaneseSan._setup()
		tokens = JapaneseSan.tokenizer_obj.tokenize(text, JapaneseSan.mode)
		return delimiter.join((token.reading_form() for token in tokens))

	@staticmethod
	def kana_to_romaji(text):
		# from https://gist.github.com/w00kie/3377492
		dictionary={
			u'きゃ':'kya',u'きゅ':'kyu',u'きょ':'kyo',
			u'しゃ':'sha',u'しゅ':'shu',u'しょ':'sho',
			u'じゃ':'ja',u'じゅ':'ju',u'じょ':'jo',
			u'にゃ':'nya',u'にゅ':'nyu',u'にょ':'nyo',
			
			u'おお':'o',u'おう':'o',
			u'こう':'ko',u'そう':'so',u'とう':'to',u'のう':'no',u'ほう':'ho',u'もう':'mo',u'ろう':'ro',
			u'ごう':'go',u'ぞう':'zo',u'どう':'do',u'ぼう':'bo',
			u'ゆう':'yu',u'よう':'yo',
			u'きょう':'kyo',u'しょう':'sho',u'ちょう':'cho',u'にょう':'nyo',u'ひょう':'hyo',u'みょう':'myo',u'りょう':'ryo',
			
			u'あ':'a',u'い':'i',u'う':'u',u'え':'e',u'お':'o',
			u'か':'ka',u'き':'ki',u'く':'ku',u'け':'ke',u'こ':'ko',
			u'さ':'sa',u'し':'shi',u'す':'su',u'せ':'se',u'そ':'so',
			u'た':'ta',u'ち':'chi',u'つ':'tsu',u'て':'te',u'と':'to',
			u'な':'na',u'に':'ni',u'ぬ':'nu',u'ね':'ne',u'の':'no',
			u'は':'ha',u'ひ':'hi',u'ふ':'fu',u'へ':'he',u'ほ':'ho',
			u'ま':'ma',u'み':'mi',u'む':'mu',u'め':'me',u'も':'mo',
			u'や':'ya',u'ゆ':'yu',u'よ':'yo',
			u'ら':'ra',u'り':'ri',u'る':'ru',u'れ':'re',u'ろ':'ro',
			u'わ':'wa',u'を':'wo',u'ん':'n',
			
			u'が':'ga',u'ぎ':'gi',u'ぐ':'gu',u'げ':'ge',u'ご':'go',
			u'ざ':'za',u'じ':'ji',u'ず':'zu',u'ぜ':'ze',u'ぞ':'zo',
			u'だ':'da',u'ぢ':'di',u'づ':'du',u'で':'de',u'ど':'do',
			u'ば':'ba',u'び':'bi',u'ぶ':'bu',u'べ':'be',u'ぼ':'bo',
			u'ぱ':'pa',u'ぴ':'pi',u'ぷ':'pu',u'ぺ':'pe',u'ぽ':'po',
			
			u'ぁ':'a',u'ぃ':'i',u'ぅ':'u',u'ぇ':'e',u'ぉ':'o',
			u'っ':'tu',
			u'ゃ':'ya',u'ゅ':'yu',u'ょ':'yo',
			u'ゎ':'wa',
			
			u'ゐ':'i',u'ゑ':'e',
			u'ー':'',
			
			u'　':' ',
			
			u'０':'0',u'１':'1',u'２':'2',u'３':'3',u'４':'4',
			u'５':'5',u'６':'6',u'７':'7',u'８':'8',u'９':'9',
			
			u'Ａ':'a',u'Ｂ':'b',u'Ｃ':'c',u'Ｄ':'d',u'Ｅ':'e',u'Ｆ':'f',u'Ｇ':'g',u'Ｈ':'h',u'Ｉ':'i',
			u'Ｊ':'j',u'Ｋ':'k',u'Ｌ':'l',u'Ｍ':'m',u'Ｎ':'n',u'Ｏ':'o',u'Ｐ':'p',u'Ｑ':'q',u'Ｒ':'r',
			u'Ｓ':'s',u'Ｔ':'t',u'Ｕ':'u',u'Ｖ':'v',u'Ｗ':'w',u'Ｘ':'x',u'Ｙ':'y',u'Ｚ':'z',
			
			u'ａ':'a',u'ｂ':'b',u'ｃ':'c',u'ｄ':'d',u'ｅ':'e',u'ｆ':'f',u'ｇ':'g',u'ｈ':'h',u'ｉ':'i',
			u'ｊ':'j',u'ｋ':'k',u'ｌ':'l',u'ｍ':'m',u'ｎ':'n',u'ｏ':'o',u'ｐ':'p',u'ｑ':'q',u'ｒ':'r',
			u'ｓ':'s',u'ｔ':'t',u'ｕ':'u',u'ｖ':'v',u'ｗ':'w',u'ｘ':'x',u'ｙ':'y',u'ｚ':'z',
		}
		
		# Sort key by length descending
		for key, value in dictionary.items():
			p = re.compile(key)
			text = p.sub(value, text)
		return text

	@staticmethod
	def san(text):
		kana = JapaneseSan.kana_readings(text, delimiter=' ')
		kana = kata2hira(kana)
		out = JapaneseSan.kana_to_romaji(kana)
		return out




def get_site(url):
	assert isinstance(url, str)
	t = urlparse(url).netloc
	t = t.split('www.')
	return t[-1].split('.')[0]


def file_san(string, lang='en'):
	if lang == "ja":
		string = JapaneseSan.san(string)
	elif not src.aux_func.valid_lang(lang):
		stringbytes = base64.urlsafe_b64encode(string.encode("utf-8"))
		string = str(stringbytes, "utf-8")

	out = sanitize_filename(string)
	out = out.replace(".", "_")
	out = out.replace(" ", "_")
	out = out.replace(",", "_")
	out = out.replace('=', '-')
	stripped = (c for c in out if 0 < ord(c) < 127)
	return ''.join(stripped)

def url_to_str_san(url):
	t = urlparse(url)
	pre = get_site(url)
	post = t.path

	assert pre
	assert post
	out = file_san(pre + post)

	assert out
	return out	

def san(string):
	no_q = html.escape(string).replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c","\"").replace(u"\u201d", "\"")
	# return re.sub(r'(?=[^\w\-_\. \[\]\(\)\?\<\>…\/,\%\$\#\!\~])(?=^"\n")', ' ',no_q)
	# return html.escape(html.unescape(string))
	# return string
	return no_q

def hyper_san(string):
	return re.sub(r'[^a-zA-Z]', '', string)