#!/usr/bin/env python3

# Import necessary modules
import os
import csv
import sys
import time
import random
import argparse

# Modules related to Lego functionality
import libbrick
import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

FAVORITE_COLUMNS = [
	'total quantity', 'item_id', 'color_name', 'name',
	'category name', 'lot value', 'sale price',
	]

#=====================
def get_set_id_from_args(args, parser):
	"""
	Return the set ID based on the given arguments.
	"""
	if args.setid is not None:
		return args.setid
	elif args.legoid is not None:
		return '{0:d}-1'.format(args.legoid)
	else:
		parser.print_help()
		sys.exit(1)

#=====================
def collect_data_for_part(part_dict, BLW, args):
	"""
	Collect and aggregate data for a specific Lego part.
	"""
	entries = part_dict['entries']

	# Check for multiple entries and print if debugging mode is on
	if len(entries) > 1:
		print(entries)
		print('too many entries')
		time.sleep(1)

	part_data_plus = entries[0]
	part_data = part_data_plus['item']

	# Initialize an empty data dictionary
	data = {}

	# Populate the data dictionary with relevant fields
	data.update(part_data_plus)
	data.update(part_data)

	# Handle different types of Lego pieces
	if part_data['type'] == 'PART':
		partID = part_data['no']
		colorID = part_data_plus['color_id']

		price_data = BLW.getPartPriceData(partID, colorID)
		data['element id'] = BLW.partIDandColorIDtoElementID(partID, colorID)
		extra_part_data = BLW.getPartData(partID)

		# partIDandColorIDtoElementID already picks an element ID with a valid image
		element_id = data.get('element id')
		data['element_image_url'] = (
			f"https://www.lego.com/cdn/product-assets/element.img.lod5photo.192x192/{element_id}.jpg"
			if element_id is not None else ''
		)

		if args.debug:
			print(price_data)

		color_data = BLW.getColorDataFromColorID(colorID)
		data.update(price_data)
		data.update(extra_part_data)
		data.update(color_data)

	elif part_data['type'] == 'MINIFIG':
		minifigID = part_data['no']
		price_data = BLW.getMinifigPriceData(minifigID)

		if args.debug:
			print(price_data)
		data.update(price_data)

	# Calculate the total quantity
	data['sale price'] = data.get('new_median_sale_price', -100)/100.0
	data['total quantity'] = data.get('extra_quantity', 0) + data.get('quantity', 0)
	data['category name'] = BLW.getCategoryName(part_data['category_id'])
	data['lot value'] = (data.get('total quantity', 1) * data.get('sale price', -1))

	# Remove fields that are long and not necessary for the CSV
	data.pop('description', None)
	data.pop('alternate_no', None)
	data.pop('item', None)
	data.pop('is_alternate', None)
	data.pop('is_counterpart', None)
	data.pop('is_obsolete', None)

	return data

def process_value(value):
	"""
	Process a single value based on its type for CSV output.

	Parameters:
		- value: The data value to be processed.

	Returns:
		- Processed value ready for CSV output.
	"""
	if isinstance(value, str):
		# Replacing problematic characters
		value = value.replace('\n', ' ')
		value = value.replace('\t', ' ')
		value = value.replace(',', ' ')
		value = value.replace('  ', ' ')
		# Truncating string if longer than 70 characters
		value = value[:70]
	elif isinstance(value, float):
		# Format the float to limit to 3 decimal places
		value = "{:.3f}".format(value)
	return value

def process_row(data, allkeys):
	"""
	Process the given data and return row of data

	Parameters:
		- data: The data dictionary containing the Lego part details.
		- allkeys: List of keys to determine the order of the columns in the CSV.
	"""
	row = []
	for key in allkeys:
		value = data.get(key, '')
		row.append(process_value(value))
	return row


def main():
	"""
	Main function to execute the script logic.
	"""
	# Set up the argument parser
	parser = argparse.ArgumentParser(description='Find Price for All Parts in a Set')

	# Two arguments: Lego ID or Set ID
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-l', '--legoid', dest='legoid', metavar='#', type=int,
		help='an integer for the Lego ID, e.g. 11011')
	group.add_argument('-s', '--setid', dest='setid', metavar='#-1', type=str,
		help='a string for the Set ID, e.g. 11011-1')
	parser.add_argument('-d', '--debug', dest='debug', action='store_true',
		help='enable debugging mode')
	#parser.set_defaults('debug', False)
	parser.add_argument('-X', '--shuffle', dest='shuffle', action='store_true',
		help='shuffle entres')
	#parser.set_defaults('shuffle', False)
	args = parser.parse_args()

	setID = get_set_id_from_args(args, parser)
	legoid = int(setID.split('-')[0])

	# Initialize the BrickLink wrapper and fetch data
	BLW = bricklink_wrapper.BrickLink()
	set_data = BLW.getSetData(setID)
	parts_tree = BLW.getPartsFromSet(setID)
	print('\nFound {0} unique parts in set {1} {2}'.format(len(parts_tree), setID, set_data['name']))
	if args.shuffle is True:
		random.shuffle(parts_tree)

	# Prepare the CSV file for data writing
	timestamp = libbrick.make_timestamp()
	output_dir = libbrick.path_utils.get_output_dir(subdir='print_out')
	csvfile = os.path.join(output_dir, "part_data_for_{0}-bricklink-{1}.csv".format(legoid, timestamp))

	with open(csvfile, 'w', newline='') as file:
		writer = csv.writer(file, delimiter='\t')
		allkeys = None
		count = 0
		total_parts = len(parts_tree)
		for part_dict in parts_tree:
			count += 1
			remaining = total_parts - count
			print(f"\n   PART {count} of {total_parts} ({remaining} remaining)")
			data = collect_data_for_part(part_dict, BLW, args)

			# Remove unused/legacy fields we no longer want to export
			data.pop('image_url', None)
			data.pop('thumbnail_url', None)
			for key in list(data.keys()):
				if key.startswith('used_'):
					data.pop(key, None)

			# Setting the columns order and writing headers
			if allkeys is None:
				datakeys = list(data.keys())
				datakeys.sort()
				allkeys = FAVORITE_COLUMNS + [key for key in datakeys if key not in FAVORITE_COLUMNS]
				writer.writerow(allkeys)
			# Process and write data to CSV
			row = process_row(data, allkeys)
			writer.writerow(row)

	BLW.close()
	print("\ncommand to open file using Finder in macos")
	print('open '+csvfile)

if __name__ == '__main__':
	main()
