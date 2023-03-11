
import typing

# -*- coding: utf-8 -*-
from typing import Generator

from pyglossary.compression import (
	# compressionOpen,
	stdCompressions,
)
from pyglossary.core import log
from pyglossary.file_utils import fileCountLines
from pyglossary.glossary_type import EntryType, GlossaryType
from pyglossary.option import (
	BoolOption,
	EncodingOption,
	NewlineOption,
	Option,
)
from pyglossary.text_reader import TextGlossaryReader, nextBlockResultType
from pyglossary.text_utils import replaceStringTable, splitByBar

enable = True
lname = "lingoes_ldf"
format = "LingoesLDF"
description = "Lingoes Source (.ldf)"
extensions = (".ldf",)
extensionCreate = ".ldf"
singleFile = True
kind = "text"
wiki = "https://en.wikipedia.org/wiki/Lingoes"
website = (
	"http://www.lingoes.net/en/dictionary/dict_format.php",
	"Lingoes.net",
)
optionsProp: "dict[str, Option]" = {
	"newline": NewlineOption(),
	"resources": BoolOption(comment="Enable resources / data files"),
	"encoding": EncodingOption(),
}


class Reader(TextGlossaryReader):
	compressions = stdCompressions

	def __len__(self: "typing.Self") -> int:
		if self._wordCount is None:
			log.debug("Try not to use len(reader) as it takes extra time")
			self._wordCount = fileCountLines(
				self._filename,
				newline=b"\n\n",
			) - self._leadingLinesCount
		return self._wordCount

	def isInfoWord(self: "typing.Self", word: str) -> bool:
		if isinstance(word, str):
			return word.startswith("#")

		return False

	def fixInfoWord(self: "typing.Self", word: str) -> str:
		if isinstance(word, str):
			return word.lstrip("#").lower()

		return word

	def nextBlock(self: "typing.Self") -> "nextBlockResultType":
		if not self._file:
			raise StopIteration
		entryLines = []
		while True:
			line = self.readline()
			if not line:
				raise StopIteration
			line = line.rstrip("\n\r")  # FIXME
			if line.startswith("###"):
				parts = line.split(":")
				key = parts[0].strip()
				value = ":".join(parts[1:]).strip()
				return key, value, None

			if line:
				entryLines.append(line)
				continue

			# now `line` is empty, process `entryLines`
			if not entryLines:
				return None
			if len(entryLines) < 2:
				log.error(
					f"invalid block near line {self._file.line}"
					f" in file {self._filename}",
				)
				return None
			word = entryLines[0]
			defi = "\n".join(entryLines[1:])
			defi = defi.replace("<br/>", "\n")  # FIXME

			word = splitByBar(word)

			return word, defi, None


class Writer(object):
	compressions = stdCompressions

	_newline: str = "\n"
	_resources: str = True

	def __init__(self: "typing.Self", glos: GlossaryType) -> None:
		self._glos = glos
		self._filename = None

	def getInfo(self: "typing.Self", key: str) -> str:
		return self._glos.getInfo(key).replace("\n", "<br>")

	def getAuthor(self: "typing.Self") -> None:
		return self._glos.author.replace("\n", "<br>")

	def finish(self: "typing.Self") -> None:
		self._filename = None

	def open(self: "typing.Self", filename: str) -> None:
		self._filename = filename

	def write(self: "typing.Self") -> "Generator[None, EntryType, None]":
		from pyglossary.text_writer import writeTxt
		newline = self._newline
		resources = self._resources
		head = (
			f"###Title: {self.getInfo('title')}\n"
			f"###Description: {self.getInfo('description')}\n"
			f"###Author: {self.getAuthor()}\n"
			f"###Email: {self.getInfo('email')}\n"
			f"###Website: {self.getInfo('website')}\n"
			f"###Copyright: {self.getInfo('copyright')}\n"
		)
		yield from writeTxt(
			self._glos,
			entryFmt="{word}\n{defi}\n\n",
			filename=self._filename,
			writeInfo=False,
			defiEscapeFunc=replaceStringTable([
				("\n", "<br/>"),
			]),
			ext=".ldf",
			head=head,
			newline=newline,
			resources=resources,
		)
