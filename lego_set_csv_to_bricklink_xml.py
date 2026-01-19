#!/usr/bin/env python3

import os
import csv
import argparse

import libbrick.path_utils

def read_csv(input_file):
	"""Read set IDs from a CSV file."""
	set_ids = []
	with open(input_file, newline='') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if row:  # Ensure row is not empty
				set_ids.append(row[0].strip())
	return set_ids

def write_xml(set_ids, output_file):
	"""Write set IDs to a BrickLink XML file."""
	with open(output_file, 'w') as xmlfile:
		xmlfile.write('<INVENTORY>\n')
		for set_id in set_ids:
			xmlfile.write('  <ITEM>\n')
			xmlfile.write('    <ITEMTYPE>S</ITEMTYPE>\n')
			xmlfile.write(f'    <ITEMID>{set_id}</ITEMID>\n')
			xmlfile.write('    <MINQTY>1</MINQTY>\n')  # Default quantity
			xmlfile.write('  </ITEM>\n')
		xmlfile.write('</INVENTORY>\n')

def main():
	parser = argparse.ArgumentParser(description="Convert a CSV of LEGO set IDs to BrickLink XML format.")
	parser.add_argument('input_file', help="Input CSV file containing LEGO set IDs")
	parser.add_argument('output_file', nargs='?', help="Output XML file", default=None)
	args = parser.parse_args()

	# Read set IDs from CSV
	set_ids = read_csv(args.input_file)
	print(f"Found {len(set_ids)} set IDs.")

	# Determine output file name
	output_file = args.output_file
	if not output_file:
		output_dir = libbrick.path_utils.get_output_dir()
		base_name = os.path.splitext(os.path.basename(args.input_file))[0]
		output_file = os.path.join(output_dir, base_name + '.xml')

	# Write set IDs to XML
	write_xml(set_ids, output_file)
	print(f"XML output written to {output_file}")

if __name__ == "__main__":
	main()
