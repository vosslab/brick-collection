#!/usr/bin/env python3

# Standard Library
import os
import sys
import time
import random
import argparse
import csv

# PIP3 modules
import lxml.etree

#==============
# BrickLink XML ↔ CSV Converter
#
# Purpose:
# ---------
# Convert between BrickLink Inventory XML and CSV formats.
#
# Supports both:
# - Inventory Uploads (new lots, no LOTID allowed)
# - Inventory Updates (editing existing lots, LOTID required)
#
# BrickLink XML Documentation:
# -----------------------------
# - Inventory Upload Format:
#   https://www.bricklink.com/help.asp?helpID=251&q=5x1
#
# - Mass Inventory Update Format:
#   https://www.bricklink.com/help.asp?helpID=198&viewType=shop
#
# XML Structure Rules:
# --------------------
# - Root element must be <INVENTORY>.
# - Contains one or more <ITEM> blocks.
#
# For Upload XML (New Inventory):
# - Each <ITEM> describes a new lot being added.
# - Allowed tags include:
#     <ITEMID>, <TYPE>, <COLOR>, <QTY>, <PRICE>, <CONDITION>, <REMARKS>, <BULK>, <RETAIN>, <STOCKROOM>, <TPID>
# - LOTID must NOT be present in Upload XML.
#
# For Update XML (Mass Update Existing Lots):
# - Each <ITEM> targets an existing lot in your store.
# - LOTID is REQUIRED for each <ITEM>.
# - Typical tags include:
#     <LOTID>, <QTY>, <PRICE>, <CONDITION>, <REMARKS>, <BULK>, <RETAIN>, <STOCKROOM>, <TPID>
# - ITEMID and COLOR are optional but can be included for reference.
#
# CSV Handling:
# -------------
# - CSV header columns are auto-mapped to XML tags (case-insensitive).
# - For Uploads: LOTID columns in CSV are ignored on output.
# - For Updates: LOTID is required in CSV for each row.
#
# Auto-Detection:
# ---------------
# - Conversion mode (xml2csv vs csv2xml) is auto-detected from input file extension unless overridden.
# - BrickLink type (upload vs update) is auto-detected by checking for LOTID presence in file contents,
#   unless overridden with --bltype flag.
#
# Usage Examples:
# ---------------
# Convert XML to CSV:
# python3 bl_inventory_converter.py --input inventory.xml
#
# Convert CSV to Update XML:
# python3 bl_inventory_converter.py --input inventory.csv --bltype update
#
# Convert CSV to Upload XML:
# python3 bl_inventory_converter.py --input inventory.csv --bltype upload
#
# Let program auto-detect both mode and bltype:
# python3 bl_inventory_converter.py --input inventory.xml
#==============


def xml_to_csv(xml_file: str, csv_file: str) -> None:
	"""
	Convert BrickLink Inventory XML to CSV.

	Args:
		xml_file (str): Path to input XML file.
		csv_file (str): Path to output CSV file.

	Returns:
		None
	"""
	tree = lxml.etree.parse(xml_file)
	root = tree.getroot()

	field_names = set()
	for item in root.findall('ITEM'):
		for elem in item:
			field_names.add(elem.tag.upper())

	field_list = sorted(field_names)

	count = 0
	type_counts = {}

	with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(field_list)

		for item in root.findall('ITEM'):
			row = []
			item_type = 'UNKNOWN'
			for field in field_list:
				element = item.find(field)
				text = element.text if element is not None else ''
				row.append(text)
				if field.upper() == 'ITEMTYPE' and text.strip():
					item_type = text.strip().upper()
			writer.writerow(row)
			count += 1
			type_counts[item_type] = type_counts.get(item_type, 0) + 1

	print(f"Processed {count} items.")
	print("Type breakdown:")
	for t, c in type_counts.items():
		print(f"  {t}: {c}")
	print(f"XML → CSV conversion complete: {csv_file}")


#==============
def csv_to_xml(csv_file: str, xml_file: str, bltype: str) -> None:
	"""
	Convert CSV back to BrickLink Inventory XML.

	Args:
		csv_file (str): Path to input CSV file.
		xml_file (str): Path to output XML file.
		bltype (str): BrickLink type, either 'upload' or 'update'.

	Returns:
		None
	"""
	root = lxml.etree.Element('INVENTORY')

	count = 0
	type_counts = {}

	with open(csv_file, newline='', encoding='utf-8') as csvfile:
		reader = csv.DictReader(csvfile)

		csv_headers = [col.upper() for col in reader.fieldnames]
		has_lotid_column = 'LOTID' in csv_headers

		for row in reader:
			lotid = row.get('LOTID', '').strip() if has_lotid_column else ''

			if bltype == 'update':
				if not lotid:
					print(f"Error: LOTID missing in update mode for row: {row}")
					sys.exit(1)

			if bltype == 'upload' and lotid:
				print(f"Warning: LOTID found in upload mode; skipping LOTID for row: {row}")

			item = lxml.etree.SubElement(root, 'ITEM')
			item_type = 'UNKNOWN'

			for field, value in row.items():
				field_upper = field.upper()
				if bltype == 'upload' and field_upper == 'LOTID':
					continue
				if value.strip():
					lxml.etree.SubElement(item, field_upper).text = value.strip()
					if field_upper == 'ITEMTYPE':
						item_type = value.strip().upper()

			count += 1
			type_counts[item_type] = type_counts.get(item_type, 0) + 1
			#time.sleep(random.random())

	tree = lxml.etree.ElementTree(root)
	tree.write(xml_file, encoding='utf-8', pretty_print=True, xml_declaration=True)

	print(f"Processed {count} items.")
	print("Type breakdown:")
	for t, c in type_counts.items():
		print(f"  {t}: {c}")
	print(f"CSV → XML conversion complete: {xml_file}")

#==============
def determine_mode(input_file: str) -> str:
	"""
	Auto-detect conversion mode based on input file extension.

	Args:
		input_file (str): Input file path.

	Returns:
		str: Conversion mode ('xml2csv' or 'csv2xml').

	Raises:
		SystemExit: If file extension is not .xml or .csv.
	"""
	ext = os.path.splitext(input_file)[1].lower()
	if ext == '.xml':
		return 'xml2csv'
	elif ext == '.csv':
		return 'csv2xml'
	else:
		print(f"Cannot determine mode from file extension: {ext}")
		sys.exit(1)


#==============
def detect_bltype(input_file: str) -> str:
	"""
	Auto-detect BrickLink type (upload or update) based on file content.

	Args:
		input_file (str): Input file path (.xml or .csv)

	Returns:
		str: 'upload' or 'update'

	Raises:
		SystemExit: If file content is unreadable or format is invalid.
	"""
	mode = determine_mode(input_file)

	if mode == 'xml2csv':
		try:
			tree = lxml.etree.parse(input_file)
			root = tree.getroot()
			for item in root.findall('ITEM'):
				if item.find('LOTID') is not None:
					return 'update'
			return 'upload'
		except Exception as e:
			print(f"Error parsing XML for bltype detection: {e}")
			sys.exit(1)

	elif mode == 'csv2xml':
		try:
			with open(input_file, newline='', encoding='utf-8') as csvfile:
				reader = csv.DictReader(csvfile)
				headers = [col.upper() for col in reader.fieldnames]
				if 'LOTID' in headers:
					return 'update'
				else:
					return 'upload'
		except Exception as e:
			print(f"Error reading CSV for bltype detection: {e}")
			sys.exit(1)

	else:
		print(f"Cannot auto-detect bltype for unknown mode: {mode}")
		sys.exit(1)


#==============
def auto_output_filename(input_file: str, mode: str) -> str:
	"""
	Generate output filename by changing file extension.

	Args:
		input_file (str): Input file path.
		mode (str): Conversion mode.

	Returns:
		str: Output file path.
	"""
	base, _ = os.path.splitext(input_file)
	if mode == 'xml2csv':
		return base + '.csv'
	else:
		return base + '.xml'


#==============
def main() -> None:
	parser = argparse.ArgumentParser(
		description='BrickLink Inventory XML ↔ CSV Converter'
	)

	parser.add_argument(
		'-i', '--input',
		dest='input_file',
		required=True,
		help='Input file path (.xml or .csv)'
	)

	parser.add_argument(
		'-o', '--output',
		dest='output_file',
		help='Output file path (optional; auto-generated if omitted)'
	)

	# Mode options
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument(
		'-m', '--mode',
		dest='mode',
		choices=['xml2csv', 'csv2xml'],
		help='Conversion mode: xml2csv or csv2xml (auto-detected if omitted)'
	)
	mode_group.add_argument(
		'-x', '--xml2csv',
		dest='mode',
		action='store_const',
		const='xml2csv',
		help='Shortcut for --mode xml2csv'
	)
	mode_group.add_argument(
		'-c', '--csv2xml',
		dest='mode',
		action='store_const',
		const='csv2xml',
		help='Shortcut for --mode csv2xml'
	)

	# BLType options
	bltype_group = parser.add_mutually_exclusive_group()
	bltype_group.add_argument(
		'-t', '--bltype',
		dest='bltype',
		choices=['upload', 'update'],
		help='BrickLink XML type: upload or update (auto-detected if omitted)'
	)
	bltype_group.add_argument(
		'--upload',
		dest='bltype',
		action='store_const',
		const='upload',
		help='Shortcut for --bltype upload'
	)
	bltype_group.add_argument(
		'--update',
		dest='bltype',
		action='store_const',
		const='update',
		help='Shortcut for --bltype update'
	)

	args = parser.parse_args()

	# Determine conversion mode
	if args.mode:
		mode = args.mode
	else:
		mode = determine_mode(args.input_file)

	detected_mode = determine_mode(args.input_file)
	if args.mode and args.mode != detected_mode:
		print(f"Warning: File extension suggests '{detected_mode}' mode, "
		      f"but you manually specified '{args.mode}'.")

	# Determine bltype (Upload vs Update)
	if args.bltype:
		bltype = args.bltype
	else:
		bltype = detect_bltype(args.input_file)
		print(f"Auto-detected bltype: {bltype}")

	# Determine output filename
	output_file = args.output_file if args.output_file else auto_output_filename(
		args.input_file,
		mode
	)

	# Run conversion
	if mode == 'xml2csv':
		xml_to_csv(args.input_file, output_file)
	elif mode == 'csv2xml':
		csv_to_xml(args.input_file, output_file, bltype)


#==============
if __name__ == '__main__':
	main()
