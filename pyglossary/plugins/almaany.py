# -*- coding: utf-8 -*-

import html
import typing

enable = True
lname = "almaany"
format = 'Almaany'
description = 'Almaany.com (SQLite3)'
extensions = ()
extensionCreate = ".db"
kind = "binary"
wiki = ""
website = (
	"https://play.google.com/store/apps/details?id=com.almaany.arar",
	"Almaany.com Arabic Dictionary - Google Play",
)

from typing import Iterator

from pyglossary.glossary_type import EntryType, GlossaryType


class Reader(object):
	def __init__(self: "typing.Self", glos: "GlossaryType") -> None:
		self._glos = glos
		self._clear()

	def _clear(self: "typing.Self") -> None:
		self._filename = ''
		self._con = None
		self._cur = None

	def open(self: "typing.Self", filename: str) -> None:
		from sqlite3 import connect
		self._filename = filename
		self._con = connect(filename)
		self._cur = self._con.cursor()
		self._glos.setDefaultDefiFormat("h")

	def __len__(self: "typing.Self") -> int:
		self._cur.execute("select count(*) from WordsTable")
		return self._cur.fetchone()[0]

	def __iter__(self: "typing.Self") -> "Iterator[EntryType]":
		from pyglossary.langs.writing_system import getWritingSystemFromText
		alternateDict = {}
		self._cur.execute("select wordkey, searchwordkey from Keys")
		for row in self._cur.fetchall():
			if row[0] in alternateDict:
				alternateDict[row[0]].append(row[1])
			else:
				alternateDict[row[0]] = [row[1]]

		self._cur.execute(
			"select word, searchword, root, meaning from WordsTable"
			" order by id",
		)
		# FIXME: iteration over self._cur stops after one entry
		# and self._cur.fetchone() returns None
		# for row in self._cur:
		for row in self._cur.fetchall():
			word = row[0]
			searchword = row[1]
			root = row[2]
			meaning = row[3]
			definition = meaning
			definition = definition.replace("|", "<br>")

			if root:
				definition += f'<br>Root: <a href="bword://{html.escape(root)}">{root}</a>'

			ws = getWritingSystemFromText(meaning)
			if ws and ws.direction == "rtl":
				definition = f'<div dir="rtl">{definition}</div>'

			words = [word, searchword]
			if word in alternateDict:
				words += alternateDict[word]
			yield self._glos.newEntry(
				words,
				definition,
				defiFormat="h",
			)

	def close(self: "typing.Self") -> None:
		if self._cur:
			self._cur.close()
		if self._con:
			self._con.close()
		self._clear()
