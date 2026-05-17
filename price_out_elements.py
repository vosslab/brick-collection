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
import libbrick.price_export
import libbrick.tui
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

#=====================
def read_element_ids_from_csv(csv_path: str) -> list:
	"""
	Read element IDs from a CSV file.

	Skips lines shorter than 4 or longer than 7 chars (after strip).
	Skips lines starting with '#'. Returns list of integers.

	Args:
		csv_path (str): Path to the CSV file.

	Returns:
		list: List of element IDs as integers.
	"""
	elementIDs = []
	with open(csv_path, 'r') as f:
		for line in f:
			sline = line.strip()
			if len(sline) < 4 or len(sline) > 7:
				continue
			if sline.startswith('#'):
				continue
			if not sline.lstrip('-').isdigit():
				continue
			elementID = int(sline)
			elementIDs.append(elementID)
	return elementIDs

#=====================
def collect_data_for_element(elementID: int, BLW, args) -> dict:
	"""
	Collect and aggregate data for a specific LEGO element.

	Args:
		elementID (int): The LEGO element ID.
		BLW: BrickLink wrapper instance.
		args: Parsed command-line arguments.

	Returns:
		dict: Dictionary with element data and image URLs.
	"""
	map_list = BLW.elementIDtoPartIDandColorID(elementID)
	if map_list is None or len(map_list) != 2:
		data = {
			'element id': elementID,
		}
		return data

	partID, colorID = map_list

	price_data = BLW.getPartPriceData(partID, colorID, min_qty=1, verbose=True)
	weighted_price = BLW.getWeightedAveragePrice(price_data, new_or_used='N')

	url = f'https://www.bricklink.com/v2/catalog/catalogitem.page?P={partID}#T=S&C={colorID}'

	data = {
		'element id': elementID,
		'BL part id': partID,
		'BL color id': colorID,
		'weighted price': weighted_price,
		'zBL url': url,
	}

	image_urls = libbrick.price_export.build_image_urls(
		element_id=elementID,
		part_id=partID,
		color_id=colorID,
		item_type='PART',
		item_id=None,
	)
	data.update(image_urls)
	priority_list = [
		image_urls['lego_image_url'],
		image_urls['rebrickable_image_url'],
		image_urls['bricklink_image_url'],
	]
	data['valid_image_url'] = libbrick.price_export.pick_valid_image_url(BLW, priority_list)

	return data

#=====================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(description='Find Price for All Elements')
	# Mutually exclusive group: csv file or single element ID
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-c', '--csv', dest='csvfile', metavar='FILE', type=str,
		help='CSV file with list of elements')
	group.add_argument('-e', '--elementid', dest='elementid', metavar='#', type=int,
		help='an integer for the element ID, e.g. 6314891')
	parser.add_argument('-d', '--debug', dest='debug', action='store_true',
		help='enable debugging mode')
	parser.add_argument('-S', '--shuffle', dest='shuffle', action='store_true',
		help='shuffle entries')
	parser.add_argument('-L', '--limit-parts', dest='limit_parts', metavar='N',
		type=int, default=None,
		help='only process the first N elements then exit')
	# Add TUI/CLI mode flags
	libbrick.tui.add_tui_args(parser)
	args = parser.parse_args()
	return args

if libbrick.tui.TEXTUAL_AVAILABLE:
	#=====================
	class ElementsApp(libbrick.tui.TaskRunnerApp):
		"""Textual TUI for pricing out LEGO elements."""

		def __init__(
			self, elementIDs: list, args: argparse.Namespace,
			BLW, csvfile: str,
		) -> None:
			title = "Pricing Elements"
			super().__init__(elementIDs, title=title)
			self.args = args
			self.BLW = BLW
			self.csvfile = csvfile
			self.allkeys = None
			self.csv_file_handle = None
			self.csv_writer = None

		def get_columns(self) -> list:
			"""Return column definitions for the elements table."""
			columns = [
				("element_id", "element_id"),
				("part_id", "part_id"),
				("color_id", "color_id"),
				("weighted_price", "weighted_price"),
			]
			return columns

		def get_row_label(self, task) -> str:
			"""Return a display label for an element row."""
			return str(task)

		def on_mount(self) -> None:
			"""Open CSV file and start tasks."""
			self.csv_file_handle = open(self.csvfile, 'w', newline='')
			self.csv_writer = csv.writer(self.csv_file_handle, delimiter='\t')
			super().on_mount()

		def process_task(self, elementID) -> tuple:
			"""Collect data for an element and write to CSV.

			Returns:
				tuple: (ok, summary, column_updates) - do NOT touch widgets here.
			"""
			data = collect_data_for_element(elementID, self.BLW, self.args)
			data = libbrick.price_export.clean_data_for_export(data)
			# Initialize column headers on first task
			if self.allkeys is None:
				self.allkeys = libbrick.price_export.build_column_order(data)
				self.csv_writer.writerow(self.allkeys)
			# Write data row to CSV
			libbrick.price_export.write_csv_row(self.csv_writer, data, self.allkeys)
			# Build summary and column update values
			element_id = data['element id']
			part_id = data.get('BL part id')  # may be missing on resolution failure
			color_id = data.get('BL color id')
			weighted_price = data.get('weighted price')
			if part_id is None:
				part_id_display = '-'
			else:
				part_id_display = str(part_id)
			if color_id is None:
				color_id_display = '-'
			else:
				color_id_display = str(color_id)
			price_text = f"{weighted_price:.3f}" if isinstance(weighted_price, (int, float)) else str(weighted_price or '-')
			# Return column updates dict for the base class to apply
			column_updates = {
				"element_id": str(element_id),
				"part_id": part_id_display,
				"color_id": color_id_display,
				"weighted_price": price_text,
			}
			summary = f"{element_id} part={part_id_display} color={color_id_display} price={price_text}"
			return True, summary, column_updates

		def cleanup(self) -> None:
			"""Close CSV file and BrickLink wrapper."""
			if self.csv_file_handle is not None:
				self.csv_file_handle.close()
				self.csv_file_handle = None
			self.BLW.close()


#=====================
def run_cli(elementIDs: list, args, BLW, csvfile: str) -> None:
	"""
	Run the plain CLI sequential processing mode.

	Args:
		elementIDs (list): List of element IDs.
		args: Parsed command-line arguments.
		BLW: BrickLink wrapper instance.
		csvfile (str): Output CSV file path.
	"""
	start_time = time.time()
	durations = []
	with open(csvfile, 'w', newline='') as file:
		writer = csv.writer(file, delimiter='\t')
		allkeys = None
		count = 0
		total_elements = len(elementIDs)
		for elementID in elementIDs:
			count += 1
			remaining = total_elements - count
			print(f"\n   ELEMENT {count} of {total_elements} ({remaining} remaining)")
			task_start = time.time()
			data = collect_data_for_element(elementID, BLW, args)
			data = libbrick.price_export.clean_data_for_export(data)
			# Setting the columns order and writing headers
			if allkeys is None:
				allkeys = libbrick.price_export.build_column_order(data)
				writer.writerow(allkeys)
			# Process and write data to CSV
			libbrick.price_export.write_csv_row(writer, data, allkeys)
			task_duration = time.time() - task_start
			durations.append(task_duration)
			# Per-element timing line
			print(f"   ({task_duration:.1f}s)")
	BLW.close()
	# Final summary: total elapsed, average per element
	elapsed = time.time() - start_time
	slow = [d for d in durations if d >= 1.0]
	if slow:
		avg = sum(slow) / len(slow)
		avg_text = f"{avg:.1f}s"
	elif durations:
		avg = sum(durations) / len(durations)
		avg_text = f"{avg:.1f}s (cached)"
	else:
		avg_text = "--"
	print()
	print("==== SUMMARY ====")
	print(f"  Elements:   {len(durations)}")
	print(f"  Elapsed:    {libbrick.common.format_duration(elapsed)}")
	print(f"  Sec/elem:   {avg_text}")


#=====================
def main():
	"""
	Main function to execute the script logic.
	"""
	args = parse_args()

	# Build element ID list from CSV or single ID
	if args.csvfile is not None and os.path.isfile(args.csvfile):
		elementIDs = read_element_ids_from_csv(args.csvfile)
		print(f"Found {len(elementIDs)} element IDs in file {args.csvfile}")
	elif args.elementid is not None:
		elementIDs = [args.elementid]
	else:
		raise ValueError("Error: must provide --csv or --elementid")

	# Initialize the BrickLink wrapper
	BLW = bricklink_wrapper.BrickLink()
	sys.stderr.write(".")

	# Shuffle if requested
	if args.shuffle:
		random.shuffle(elementIDs)

	# Limit elements for testing
	if args.limit_parts is not None:
		elementIDs = elementIDs[:args.limit_parts]
		print(f"Limiting to {len(elementIDs)} elements")

	# Prepare the CSV file for data writing
	timestamp = libbrick.common.make_timestamp()
	output_dir = libbrick.path_utils.get_output_dir(subdir='print_out')
	csvfile = os.path.join(output_dir, f"element_price_data-bricklink-{timestamp}.csv")

	# Choose TUI or CLI mode
	if libbrick.tui.should_use_tui(args):
		app = ElementsApp(elementIDs, args, BLW, csvfile)
		app.run()
		# Cleanup after TUI exits
		app.cleanup()
	else:
		run_cli(elementIDs, args, BLW, csvfile)

	# Always report the output path so the user can find it
	print()
	print(f"Wrote output to: {csvfile}")
	print(f"  open {csvfile}")

if __name__ == '__main__':
	main()
