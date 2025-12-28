#!/usr/bin/env python3

# Standard Library
import os
import sys
import argparse

# Local Repo Modules
import libbrick
import libbrick.path_utils
import libbrick.wrappers.rebrick_wrapper as rebrick_wrapper
import libbrick.wrappers.brickset_wrapper as brickset_wrapper
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

#============================
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

	# Get data from 'rbw' source, prefix keys with 'rb_', and merge into the data dictionary
	rbw_data = rbw.getSetDataDirect(setID)
	if rbw_data is not None:
		rbw_prefixed_data = libbrick.add_prefix_to_dict_keys(rbw_data, 'rb_')
		data |= rbw_prefixed_data

	# Get data from 'bsw' source, prefix keys with 'bs_', and merge into the data dictionary
	bsw_data = bsw.getSetDataDirect(setID)
	if bsw_data is not None:
		bsw_prefixed_data = libbrick.add_prefix_to_dict_keys(bsw_data, 'bs_')
		data |= bsw_prefixed_data

	# Get data from 'blw' source, prefix keys with 'bl_', and merge into the data dictionary
	blw_data = blw.getSetDataDirect(setID)
	blw_prefixed_data = libbrick.add_prefix_to_dict_keys(blw_data, 'bl_')
	data |= blw_prefixed_data

	# Get price data from 'blw' source, prefix keys with 'bl_', and merge into the data dictionary
	blw_price_data = blw.getSetPriceData(setID)
	blw_price_prefixed_data = libbrick.add_prefix_to_dict_keys(blw_price_data, 'bl_')
	data |= blw_price_prefixed_data

	# Add the MSRP from 'bsw' source directly to the data dictionary
	data['msrp'] = bsw.getSetMSRP(setID)
	#print(data)

	data['bl_num_minifigs'] = len(blw.getMinifigIDsFromSet(setID, verbose=False))

	libbrick.process_data(data)

	return data

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
	csvfile = os.path.join(output_dir, f"set_data-gimme-{timestamp}.csv")

	#============================
	#============================

	line = 0
	data_tree = []

	#============================
	# Process each itemID in the setIDs list
	for itemID in setIDs:
		print(f"--- itemID: {itemID}")
		line += 1
		sys.stderr.write(".")
		data = getAllData(itemID, rbw, bsw, blw)
		if data is None:
			continue
		data_tree.append(data)
		if line % 100 == 0:
			rbw.save_cache()
			bsw.save_cache()
			blw.save_cache()

	#random.shuffle(data_tree)
	rbw.close()
	bsw.close()
	blw.close()

	#============================
	#============================
	libbrick.write_data_to_csv(data_tree, csvfile)

	#============================
	#============================

	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(line, csvfile)))

	print(("open %s"%(csvfile)))
