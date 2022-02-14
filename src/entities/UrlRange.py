from dataclasses import dataclass, field

@dataclass(frozen=True)
class UrlRange:
	startUrl: str
	endUrl: str

@dataclass(frozen=True)
class UrlRangeSet:
	ranges: tuple = field(default_factory=tuple)

	def __post_init__(self):
		for u_range in self.ranges:
			assert type(u_range) is UrlRange, f'{u_range = } (is not type UrlRange)'