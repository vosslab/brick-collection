#!/usr/bin/env python3

import os
import sys

import libbrick
import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

#============================
#============================
def write_header(setID: str, BLW: bricklink_wrapper.BrickLink) -> list:
	"""
	Write the header row to the CSV file.

	Args:
		setID: LEGO set ID.
		BLW: Instance of BrickLink API wrapper.

	Returns:
		List of keys for the data dictionary.
	"""
	data = BLW.getSetData(setID)
	data = BLW.getSetDataDetails(setID)
	allkeys = list(data.keys())
	allkeys.sort()
	print(', '.join(allkeys))
	return allkeys

#============================
#============================
def get_set_data_output(setID: str, BLW: bricklink_wrapper.BrickLink, allkeys: list) -> str:
	"""
	Get data output string for a single LEGO set.

	Args:
		setID: LEGO set ID.
		BLW: Instance of BrickLink API wrapper.
		allkeys: List of keys for the data dictionary.

	Returns:
		Data output string.
	"""
	sys.stderr.write(".")
	data = BLW.getSetData(setID)
	data = BLW.getSetDataDetails(setID)
	output = ""

	row = []
	for key in allkeys:
		try:
			row.append(str(data[key]))
		except KeyError:
			print(f"missing key: {key}")
			row.append("")
	output += "\t".join(row) + "\n"

	return output

#============================
#============================
def main():
	"""
	Main function to look up LEGO set data using BrickLink API.
	"""
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)
	setIDFile = sys.argv[1]
	if not os.path.isfile(setIDFile):
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)

	setIDs = libbrick.read_setIDs_from_file(setIDFile)
	timestamp = libbrick.make_timestamp()

	output_dir = libbrick.path_utils.get_output_dir(subdir='lookup')
	csvfile = os.path.join(output_dir, f"set_data-bricklink-{timestamp}.csv")
	line_count = 0

	BLW = bricklink_wrapper.BrickLink()
	with open(csvfile, "w") as f:
		allkeys = write_header(setIDs[0], BLW)
		f.write("\t".join(allkeys) + "\n")

		for setID in setIDs:
			if not '-' in setID:
				setID = str(setID) + "-1"
			line_count += 1
			output = get_set_data_output(setID, BLW, allkeys)
			f.write(output)

	BLW.close()
	sys.stderr.write("\n")
	print(f"Wrote {line_count} lines to {csvfile}")

	print(f"open \"{csvfile}\"")

#============================
#============================
if __name__ == '__main__':
	main()
