

# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from typing import TypeAlias


MultiStr: "TypeAlias" = "str | list[str]"


class BaseEntry:
	__slots__: "list[str]" = []

	def __init__(self) -> None:
		self._word: "str | list[str]"

	@property
	def s_word(self) -> str:
		raise NotImplementedError

	@property
	def defi(self) -> str:
		raise NotImplementedError

	@property
	def b_word(self) -> bytes:
		"""
			returns bytes of word,
				and all the alternate words
				separated by b"|"
		"""
		return self.s_word.encode("utf-8")

	@property
	def b_defi(self) -> bytes:
		"""
			returns bytes of definition,
				and all the alternate definitions
				separated by b"|"
		"""
		return self.defi.encode("utf-8")
