from dataclasses import dataclass, field


@dataclass(order=True, frozen=True)
class Chapter(object):
	"""Class that all parsers should return """
	number: int = field(repr=False)
	title: str
	content: str = field(repr=False)
	images: set = field(default_factory=set, repr=False,
	                    hash=False, compare=False)
 
	def ghash(self):
		return hex(abs(hash(self)))[2:]


