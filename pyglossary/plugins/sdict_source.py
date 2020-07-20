# -*- coding: utf-8 -*-
# Source Glossary for "Sdictionary" (http://sdict.org)
# It has extension ".sdct"

from formats_common import *

enable = True
format = "SdictSource"
description = "Sdictionary Source (sdct)"
extensions = (".sdct",)
singleFile = True
optionsProp = {
	"writeInfo": BoolOption(),
	"newline": NewlineOption(),
	"resources": BoolOption(),
}
depends = {}

tools = [
	{
		"name": "PTkSdict",
		"web": "http://swaj.net/sdict/create-dicts.html",
		"platforms": ["Linux", "Windows", "Mac"],
		"license": "GPL",
	},
]


class Writer(object):
	def __init__(self, glos: GlossaryType) -> None:
		self._glos = glos

	def write(
		self,
		filename,
		writeInfo=True,
		newline="\n",
		resources=True,
	) -> Generator[None, "BaseEntry", None]:
		glos = self._glos
		head = ""
		if writeInfo:
			head += "<header>\n"
			for name, infoKey in (
				("title", "name"),
				("author", "author"),
				("description", "description"),
				("w_lang", "sourceLang"),
				("a_lang", "targetLang"),
			):
				head += name + " = " + glos.getInfo(infoKey) + "\n"
			head += "</header>\n#\n#\n#\n"
		yield from glos.writeTxt(
			entryFmt="{word}___{defi}\n",
			filename=filename,
			writeInfo=False,
			defiEscapeFunc=replaceStringTable([
				("\n", "<BR>"),
			]),
			ext=".sdct",
			head=head,
			newline=newline,
			resources=resources,
		)
