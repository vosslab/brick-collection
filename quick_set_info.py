#!/usr/bin/env python3

# Standard Library
import os
import sys
import math
import time
import argparse

# Local Repo Modules
import libbrick
import libbrick.path_utils
import libbrick.wrappers.rebrick_wrapper as rebrick_wrapper
import libbrick.wrappers.brickset_wrapper as brickset_wrapper
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

## INFO WANTS
# Set ID
# Theme
# Subtheme
# Set Name
# Year Released
# MSRP
# New Value (Month-Year)
# Used Value (Month-Year)
# Growth
# Type: Set
# Number of Pieces
# Image URL
# Number of Minifigs


#============================
def getAllData(setID: str, rbw, bsw, blw) -> dict:
	"""
	Gathers all data for a given set ID from multiple sources, adds prefixes to the keys,
	and combines the results into a single dictionary.

	Args:
		setID (str): The identifier for the set, e.g., '10240-1'.
		rbw: The object providing data from the 'rbw' source.
		bsw: The object providing data from the 'bsw' source.
		blw: The object providing data from the 'blw' source.

	Returns:
		dict: A dictionary containing the combined data with prefixed keys.
	"""
	data = {}

	# Get data from 'rbw' source and prefix keys with 'rb_'
	rbw_data = rbw.getSetDataDirect(setID)
	if rbw_data is not None:
		data |= libbrick.add_prefix_to_dict_keys(rbw_data, 'rb_')

	# Get data from 'blw' source and prefix keys with 'bl_'
	blw_data = blw.getSetDataDirect(setID)
	data |= libbrick.add_prefix_to_dict_keys(blw_data, 'bl_')

	# Get price data from 'blw' source and prefix keys with 'bl_'
	blw_price_data = blw.getSetPriceData(setID)
	data |= libbrick.add_prefix_to_dict_keys(blw_price_data, 'bl_')

	# Add the MSRP from 'bsw' source directly to the data dictionary
	data['msrp'] = bsw.getSetMSRP(setID)

	data['bl_num_minifigs'] = len(blw.getMinifigIDsFromSet(setID, verbose=True))

	libbrick.process_data(data)

	return data


#============================
#============================
def find_first_valid_key(data_dict: dict, key_list: list) -> str:
	"""
	Finds the first key in key_list that exists in data_dict and returns its value.
	If no valid key is found, returns an empty string.

	Args:
		data_dict (dict): The original data dictionary.
		key_list (list): A list of potential keys.

	Returns:
		str: The value of the first valid key found, or an empty string if none are found.
	"""
	number_flag = False
	for original_key_name in key_list:
		value = data_dict.get(original_key_name)
		if value is not None:
			if isinstance(value, (int, float)):
				number_flag = True
				if value > 0:
					return value
			else:
				# If conversion fails, return the value as is
				return value
	if number_flag is True:
		return -1
	return ''

#============================
#============================
def filter_data_dict(data_dict: dict, data_mapping: dict) -> dict:
	"""
	Filters and maps data from the input dictionary to a new dictionary with specific keys.
	Args:
		data_dict (dict): The original data dictionary.
	Returns:
		dict: A filtered and mapped data dictionary.
	"""
	# Initialize the filtered data dictionary
	filtered_data_dict = {}

	# Iterate through the data mapping and populate the filtered dictionary
	for key_name, map_value in data_mapping.items():
		if isinstance(map_value, list):
			# Find the first valid key and set the corresponding value
			filtered_data_dict[key_name] = find_first_valid_key(data_dict, map_value)
		elif isinstance(map_value, str):
			# Directly map the value if it's a string
			filtered_data_dict[key_name] = data_dict.get(map_value, '')
		else:
			# Set a default empty value
			filtered_data_dict[key_name] = ''

	return filtered_data_dict

#============================
#============================
def parse_arguments() -> argparse.Namespace:
	"""
	Parse command-line arguments using argparse.

	Returns:
		argparse.Namespace: The parsed command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description='Fetch LEGO set data from various sources using a setID, LEGO ID, or a CSV file of IDs.'
	)
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument(
		'-c', '--csv',
		dest='csvfile',
		help='Path to the CSV file containing LEGO IDs.',
		type=str
	)
	group.add_argument(
		'-l', '--legoid',
		dest='legoid',
		help='A single LEGO ID (integer).',
		type=int
	)
	group.add_argument(
		'-s', '--setid',
		dest='setid',
		help='A single setID (string, e.g., "10240-1").',
		type=str
	)

	return parser.parse_args()

#============================
#============================
def is_power_of_two_or_special(item_count: int) -> bool:
	"""
	Determine if the item count is a power of two up to 64 or every 100 thereafter.
	Args:
		item_count (int): The current item count.
	Returns:
		bool: True if the cache should be saved, False otherwise.
	"""
	# Check if the item count is a power of two up to 64
	if math.log2(item_count).is_integer():
		return True
	# Check if the item count is a multiple of 100
	if item_count % 100 == 0:
		return True
	return False

#============================
#============================
if __name__ == '__main__':
	# Parse the command-line arguments
	args = parse_arguments()

	# Initialize the wrappers
	rbw = rebrick_wrapper.Rebrick()
	bsw = brickset_wrapper.BrickSet()
	blw = bricklink_wrapper.BrickLink()

	# Initialize the setIDs list
	setIDs = []

	if args.csvfile:
		# Validate the CSV file
		if not os.path.isfile(args.csvfile):
			print(f"Error: The file '{args.csvfile}' does not exist.")
			sys.exit(1)

		# Read set IDs from the file
		setIDs = libbrick.read_setIDs_from_file(args.csvfile)

	elif args.legoid:
		# Convert the LEGO ID to a setID string format and add it to the list
		setID = f"{args.legoid}-1"
		setIDs.append(setID)

	elif args.setid:
		# Add the provided setID directly to the list
		setIDs.append(args.setid)

	#============================
	#============================
	timestamp = libbrick.make_timestamp()
	output_dir = libbrick.path_utils.get_output_dir()
	csvfile = os.path.join(output_dir, f"quick_set_info-{timestamp}.csv")

	#============================
	#============================
	# Get the current date code (month and year)
	date_code = time.strftime("(%b %Y)", time.localtime())

	# Define the mapping between desired keys and the original keys in the data dictionary
	data_mapping = {
		'Set ID': ['rb_set_id', 'rb_set_num', 'bl_item_id', 'bl_no',],
		'Theme': ['bl_category_name', 'rb_theme_name', 'bs_theme'],
		#'SubTheme': ['', '', 'subtheme'],  # Uncomment and define if needed
		'Set Name': ['bl_name', 'rb_name', 'bs_name', ],
		'Release Year': ['bl_year_released', 'rb_year', 'bs_year',],
		'Retail Price (MSRP)': 'msrp',
		'New Value ' + date_code: ['bl_new_median_sale_price', 'bl_new_median_list_price'],
		'Used Value ' + date_code: ['bl_used_median_sale_price', 'bl_used_median_list_price'],
		'New Growth ' + date_code: 'growth-new',
		'Type': 'bl_type',
		'Number of Pieces': ['rb_num_parts', 'bs_pieces'],
		'Image URL': ['bl_image_url', 'rb_set_img_url', 'bs_image.imageURL'],
		'Number of Minifigs': ['bl_num_minifigs', 'bs_minifigs']
	}
	key_order = tuple(data_mapping.keys())
	#print(key_order)

	#============================
	#============================

	item_count = 0
	data_tree = []

	#============================
	# Process each itemID in the setIDs list
	# Processing the setIDs
	for itemID in setIDs:
		print(f"--- itemID: {itemID}")
		item_count += 1
		sys.stderr.write(".")
		data = getAllData(itemID, rbw, bsw, blw)
		if data is None:
			continue

		# Process and filter data
		filter_data = filter_data_dict(data, data_mapping)
		filter_data['Retail Price (MSRP)'] /= 100
		filter_data['New Value ' + date_code] /= 100
		filter_data['Used Value ' + date_code] /= 100

		data_tree.append(filter_data)

		# Save cache if the item count meets the criteria
		if is_power_of_two_or_special(item_count):
			rbw.save_cache()
			bsw.save_cache()
			blw.save_cache()

	#random.shuffle(data_tree)
	rbw.close()
	bsw.close()
	blw.close()

	#============================
	#============================
	libbrick.write_data_to_csv(data_tree, csvfile, key_order)

	#============================
	#============================

	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(len(data_tree), csvfile)))
	print(("open %s"%(csvfile)))
