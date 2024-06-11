#!/usr/bin/env python3

import os
import sys

import libbrick
import rebrick_wrapper

#============================
#============================
def write_header(setID: str, RBW: rebrick_wrapper.Rebrick) -> list:
	"""
	Write the header row to the CSV file.

	Args:
		setID: LEGO set ID.
		RBW: Instance of Rebrick API wrapper.

	Returns:
		List of keys for the data dictionary.
	"""
	data = RBW.getSetData(setID)
	allkeys = list(data.keys())
	allkeys.sort()
	print(', '.join(allkeys))
	return allkeys

#============================
#============================
def get_set_data_output(setID: str, RBW: rebrick_wrapper.Rebrick, allkeys: list) -> str:
	"""
	Get data output string for a single LEGO set.

	Args:
		setID: LEGO set ID.
		RBW: Instance of Rebrick API wrapper.
		allkeys: List of keys for the data dictionary.

	Returns:
		Data output string.
	"""
	sys.stderr.write(".")
	data = RBW.getSetData(setID)
	output = ""

	row = []
	for key in allkeys:

		try:
			if '{' in str(data.get(key, "")):
				row.append("")
				continue
			row.append(str(data[key]).replace('\n', ''))

		except KeyError:
			print(f"missing key: {key}")
			row.append("")
	output += "\t".join(row) + "\n"

	return output

#============================
#============================
def main():
	"""
	Main function to look up LEGO set data using Rebrick API.
	"""
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <txt file with lego IDs>")
		sys.exit(1)
	setIDFile = sys.argv[1]
	if not os.path.isfile(setIDFile):
		print("usage: ./lookupLego.py <txt file with lego IDs>")
		sys.exit(1)

	setIDs = libbrick.read_setIDs_from_file(setIDFile)
	timestamp = libbrick.make_timestamp()

	csvfile = f"set_data-rebrick-{timestamp}.csv"
	line_count = 0

	RBW = rebrick_wrapper.Rebrick()
	with open(csvfile, "w") as f:
		allkeys = write_header(setIDs[0], RBW)
		f.write("\t".join(allkeys) + "\n")

		for setID in setIDs:
			if not '-' in setID:
				setID = str(setID) + "-1"
			line_count += 1
			output = get_set_data_output(setID, RBW, allkeys)
			f.write(output)

	RBW.close()
	sys.stderr.write("\n")
	print(f"Wrote {line_count} lines to {csvfile}")

	print(f"open {csvfile}")

#============================
#============================
if __name__ == '__main__':
	main()
