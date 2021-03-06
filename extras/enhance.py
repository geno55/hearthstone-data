#!/usr/bin/env python

import os
import re
FIREPLACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
import sys; sys.path.append(FIREPLACE_DIR)
from xml.dom import minidom
from xml.etree import ElementTree

from fireplace.cards import cardxml
from fireplace.enums import GameTag
import chooseone


def add_chooseone_tags(card, ids):
	for id in ids:
		e = ElementTree.Element("ChooseCard")
		e.attrib["cardID"] = id
		card.xml.append(e)
	print("%s: Adding Choose One cards: %r" % (card.name, ids))


def add_cant_attack_tag(card):
	e = ElementTree.Element("Tag")
	e.attrib["value"] = "1"
	e.attrib["Type"] = "Bool"
	e.attrib["enumID"] = str(int(GameTag.CANT_ATTACK))
	card.xml.append(e)
	print("%s: Setting GameTag.CANT_ATTACK" % (card.name))


def guess_spellpower(card):
	sre = re.search(r"Spell Damage \+(\d+)", card.description)
	dmg = int(sre.groups()[0])
	e = card._findTag(GameTag.SPELLPOWER)[0]
	e.attrib["value"] = str(dmg)
	print("%s: Setting Spell Power to %i" % (card.name, dmg))


def guess_overload(card):
	sre = re.search(r"Overload[^(]+\((\d+)\)", card.description)
	amount = int(sre.groups()[0])
	e = card._findTag(GameTag.RECALL)[0]
	e.attrib["value"] = str(amount)
	print("%s: Setting Overload to %i" % (card.name, amount))


def main():
	db, xml = cardxml.load(os.path.join(FIREPLACE_DIR, "data", "TextAsset", "enUS.txt"))
	for id, card in db.items():
		if hasattr(chooseone, id):
			add_chooseone_tags(card, getattr(chooseone, id))

		if card.tags.get(GameTag.SPELLPOWER):
			guess_spellpower(card)

		if card.tags.get(GameTag.RECALL):
			guess_overload(card)

		if "Can't Attack." in card.description:
			add_cant_attack_tag(card)

	# xml = db[next(db.__iter__())].xml
	with open(os.path.join(FIREPLACE_DIR, "data", "enUS.xml"), "w") as f:
		root = ElementTree.Element("CardDefs")
		for e in xml.findall("Entity"):
			# We want to retain the order so we can't just use db.keys()
			id = e.attrib["CardID"]
			card = db[id]
			root.append(card.xml)

		outstr = ElementTree.tostring(root)
		# Reparse for clean indentation
		outstr = minidom.parseString(outstr).toprettyxml(indent="\t")
		outstr = "\n".join(line for line in outstr.split("\n") if line.strip())
		f.write(outstr)
		print("Written to", f.name)


if __name__ == "__main__":
	main()
