#!/usr/bin/env python3

# Standard Library
import os
import csv
import sys
import time
import random
import argparse

# local repo modules
import libbrick.common
import libbrick.path_utils
import libbrick.tui
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


#=====================
def clean_data_for_export(data: dict) -> dict:
	"""
	Remove unused/legacy fields from data before CSV export.

	Args:
		data (dict): The raw data dictionary.

	Returns:
		dict: The cleaned data dictionary.
	"""
	data.pop('image_url', None)
	data.pop('thumbnail_url', None)
	# Remove all used_ prefix keys
	for key in list(data.keys()):
		if key.startswith('used_'):
			data.pop(key, None)
	return data


#=====================
def write_csv_row(writer, data: dict, allkeys: list) -> None:
	"""
	Write a single data row to the CSV writer.

	Args:
		writer: csv.writer object.
		data (dict): The data dictionary for this row.
		allkeys (list): Column key ordering.
	"""
	row = process_row(data, allkeys)
	writer.writerow(row)


#=====================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(description='Find Price for All Parts in a Set')
	# Two arguments: Lego ID or Set ID
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-l', '--legoid', dest='legoid', metavar='#', type=int,
		help='an integer for the Lego ID, e.g. 11011')
	group.add_argument('-s', '--setid', dest='setid', metavar='#-1', type=str,
		help='a string for the Set ID, e.g. 11011-1')
	parser.add_argument('-d', '--debug', dest='debug', action='store_true',
		help='enable debugging mode')
	parser.add_argument('-S', '--shuffle', dest='shuffle', action='store_true',
		help='shuffle entries')
	parser.add_argument('-L', '--limit-parts', dest='limit_parts', metavar='N',
		type=int, default=None,
		help='only process the first N parts then exit')
	# Add TUI/CLI mode flags
	libbrick.tui.add_tui_args(parser)
	args = parser.parse_args()
	return args


if libbrick.tui.TEXTUAL_AVAILABLE:
	#=====================
	class PartsInSetApp(libbrick.tui.TaskRunnerApp):
		"""Textual TUI for pricing out parts in a LEGO set."""

		def __init__(
			self, tasks: list, args: argparse.Namespace,
			BLW, setID: str, set_data: dict, csvfile: str,
		) -> None:
			title = f"Parts in Set {setID} - {set_data.get('name', '')}"
			super().__init__(tasks, title=title)
			self.args = args
			self.BLW = BLW
			self.setID = setID
			self.set_data = set_data
			self.csvfile = csvfile
			self.allkeys = None
			self.csv_file_handle = None
			self.csv_writer = None

		def get_columns(self) -> list:
			"""Return column definitions for the parts table."""
			columns = [
				("item_id", "item_id"),
				("color", "color"),
				("sale_price", "sale price"),
				("lot_value", "lot value"),
				("name", "name", 40),
			]
			return columns

		def get_row_label(self, task) -> str:
			"""Return a display label for a part row."""
			entries = task.get('entries', [])
			if entries:
				item = entries[0].get('item', {})
				item_id = item.get('no', '???')
				return str(item_id)
			return "???"

		def on_mount(self) -> None:
			"""Open CSV file and start tasks."""
			self.csv_file_handle = open(self.csvfile, 'w', newline='')
			self.csv_writer = csv.writer(self.csv_file_handle, delimiter='\t')
			super().on_mount()

		def process_task(self, task) -> tuple:
			"""Collect data for a part and write to CSV.

			Returns:
				tuple: (ok, summary, column_updates) - do NOT touch widgets here.
			"""
			data = collect_data_for_part(task, self.BLW, self.args)
			data = clean_data_for_export(data)
			# Initialize column headers on first task
			if self.allkeys is None:
				datakeys = sorted(data.keys())
				self.allkeys = FAVORITE_COLUMNS + [
					key for key in datakeys if key not in FAVORITE_COLUMNS
				]
				self.csv_writer.writerow(self.allkeys)
			# Write data row to CSV
			write_csv_row(self.csv_writer, data, self.allkeys)
			# Build summary and column update values
			item_id = data.get('no', '???')
			color_name = str(data.get('color_name', ''))[:20]
			name = str(data.get('name', ''))[:60]
			sale_price = data.get('sale price', 0)
			lot_value = data.get('lot value', 0)
			sale_text = f"${sale_price:.2f}" if isinstance(sale_price, (int, float)) else str(sale_price)
			lot_text = f"${lot_value:.2f}" if isinstance(lot_value, (int, float)) else str(lot_value)
			# Return column updates dict for the base class to apply
			column_updates = {
				"item_id": str(item_id),
				"color": color_name,
				"name": name,
				"sale_price": sale_text,
				"lot_value": lot_text,
			}
			summary = f"{item_id} {color_name} {name} sale={sale_text} lot={lot_text}"
			return True, summary, column_updates

		def cleanup(self) -> None:
			"""Close CSV file and BrickLink wrapper."""
			if self.csv_file_handle is not None:
				self.csv_file_handle.close()
				self.csv_file_handle = None
			self.BLW.close()


#=====================
def run_cli(parts_tree: list, args, BLW, csvfile: str) -> None:
	"""
	Run the plain CLI sequential processing mode.

	Args:
		parts_tree (list): List of part dictionaries.
		args: Parsed command-line arguments.
		BLW: BrickLink wrapper instance.
		csvfile (str): Output CSV file path.
	"""
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
			data = clean_data_for_export(data)
			# Setting the columns order and writing headers
			if allkeys is None:
				datakeys = sorted(data.keys())
				allkeys = FAVORITE_COLUMNS + [
					key for key in datakeys if key not in FAVORITE_COLUMNS
				]
				writer.writerow(allkeys)
			# Process and write data to CSV
			write_csv_row(writer, data, allkeys)
	BLW.close()
	print("\ncommand to open file using Finder in macos")
	print('open ' + csvfile)


#=====================
def main():
	"""
	Main function to execute the script logic.
	"""
	args = parse_args()
	# Build a temporary parser for get_set_id_from_args error handling
	parser = argparse.ArgumentParser()
	setID = get_set_id_from_args(args, parser)
	legoid = int(setID.split('-')[0])

	# Initialize the BrickLink wrapper and fetch data
	BLW = bricklink_wrapper.BrickLink()
	set_data = BLW.getSetData(setID)
	parts_tree = BLW.getPartsFromSet(setID)
	print(f"\nFound {len(parts_tree)} unique parts in set {setID} {set_data['name']}")
	if args.shuffle is True:
		random.shuffle(parts_tree)
	# Limit parts for testing
	if args.limit_parts is not None:
		parts_tree = parts_tree[:args.limit_parts]
		print(f"Limiting to {len(parts_tree)} parts")

	# Prepare the CSV file for data writing
	timestamp = libbrick.common.make_timestamp()
	output_dir = libbrick.path_utils.get_output_dir(subdir='print_out')
	csvfile = os.path.join(output_dir, f"part_data_for_{legoid}-bricklink-{timestamp}.csv")

	# Choose TUI or CLI mode
	if libbrick.tui.should_use_tui(args):
		app = PartsInSetApp(parts_tree, args, BLW, setID, set_data, csvfile)
		app.run()
		# Cleanup after TUI exits
		app.cleanup()
	else:
		run_cli(parts_tree, args, BLW, csvfile)

if __name__ == '__main__':
	main()
