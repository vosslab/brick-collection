
import os
import re
import csv
import time
import string
from collections.abc import MutableMapping

#============================
#============================
def add_prefix_to_dict_keys(original_dict: dict, prefix: str) -> dict:
	"""
	Adds a prefix to all keys in the provided dictionary.

	Args:
		original_dict (dict): The dictionary whose keys will be prefixed.
		prefix (str): The string prefix to add to each key.

	Returns:
		dict: A new dictionary with the prefixed keys.
	"""
	# Create a new dictionary with prefixed keys
	prefixed_dict = {f"{prefix}{key}": value for key, value in original_dict.items()}
	return prefixed_dict


#============================
#============================
def _flatten_dict_gen(d: MutableMapping, parent_key: str, sep: str):
	"""
	Generator function to flatten a nested dictionary.

	Args:
		d (MutableMapping): The dictionary to flatten.
		parent_key (str): The base key to prepend to the flattened keys.
		sep (str): The separator to use between keys.

	Yields:
		Tuple[str, Any]: The flattened key-value pairs.
	"""
	for k, v in d.items():
		new_key = parent_key + sep + k if parent_key else k
		if isinstance(v, MutableMapping):
			yield from _flatten_dict_gen(v, new_key, sep=sep)
		else:
			yield new_key, v

#============================
#============================
def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.') -> dict:
	"""
	Flattens a nested dictionary.

	Args:
		d (MutableMapping): The dictionary to flatten.
		parent_key (str, optional): The base key to prepend to the flattened keys. Defaults to ''.
		sep (str, optional): The separator to use between keys. Defaults to '.'.

	Returns:
		dict: The flattened dictionary.
	"""
	return dict(_flatten_dict_gen(d, parent_key, sep))

#============================
#============================
def clean_value(value: str) -> str:
	"""
	Cleans a string value by removing tabs, newlines, and commas,
	trimming extra spaces, and truncating long values.

	Args:
		value (str): The string value to clean.

	Returns:
		str: The cleaned string value.
	"""
	# Convert to string and strip leading/trailing whitespace
	value = str(value).strip()

	# Replace problematic characters
	value = value.replace('\t', ' ')
	value = value.replace('\n', ' ')
	value = value.replace(',', ' ')

	# Remove extra spaces
	while '  ' in value:
		value = value.replace('  ', ' ')

	if value.startswith('//') and '.com' in value:
		value = 'https:' + value

	# Truncate if too long
	if len(value) > 100:
		value = value[:100]

	return value

#============================
#============================
def write_data_to_csv(data_tree: list, csvfile: str, key_order: list=None) -> None:
	"""
	Writes data to a CSV file, flattening nested dictionaries and ensuring all keys are included.

	Args:
		data_tree (list): A list of dictionaries, each representing a row of data to be written.
		csvfile (str): The file path to write the CSV data.

	Returns:
		None
	"""
	# Step 1: Flatten each dictionary, clean values, and gather all unique keys
	allkeys = set()
	flattened_tree = []

	for data in data_tree:
		flat_data = flatten_dict(data)

		# Clean each value in the flattened dictionary
		cleaned_flat_data = {k: clean_value(v) for k, v in flat_data.items()}

		flattened_tree.append(cleaned_flat_data)
		allkeys.update(cleaned_flat_data.keys())

	# Convert the set of keys to a sorted list
	allkeys = sorted(allkeys, key=str.lower)

	if key_order is None:
		key_order = allkeys

	# Step 2: Write the CSV file using the csv module
	with open(csvfile, "w", newline='') as f:
		writer = csv.DictWriter(f, fieldnames=key_order, delimiter='\t')

		# Write the header row
		writer.writeheader()

		# Write the data rows
		for flat_data in flattened_tree:
			writer.writerow(flat_data)

#============================
#============================
def process_data(data: dict) -> dict:
	"""
	Processes the data dictionary to calculate additional fields and set flags based on conditions.

	Args:
		data (dict): The original data dictionary to be processed.

	Returns:
		dict: The updated data dictionary with additional fields and flags.
	"""

	# Ensure numparts is valid
	numparts = data.get('bl_num_parts', 1)
	if numparts <= 0:
		numparts = 1

	# Calculate price-per-part and growth rates if MSRP is available
	if data.get('msrp') is not None and data.get('msrp') > 0:
		data['$pP-retail'] = round(data.get('msrp', 0) / numparts, 1)
		data['growth-used'] = round(data.get('bl_used_median_sale_price', 0) / data['msrp'], 3)
		data['growth-new'] = round(data.get('bl_new_median_sale_price', 0) / data['msrp'], 3)
	else:
		data['$pP-retail'] = 0
		data['growth-used'] = 1.0
		data['growth-new'] = 1.0

	# Calculate used and new price-per-part
	data['$pP-used'] = round(data.get('bl_used_median_sale_price', 0) / numparts, 1)
	data['$pP-new'] = round(data.get('bl_new_median_sale_price', 0) / numparts, 1)

	# Determine the flag based on calculated values
	if data['$pP-used'] > 10 and data['growth-used'] > 1.5:
		data['flag'] = "KEEP"
	elif data.get('rb_year', 0) >= 2019:
		data['flag'] = "wait"
	elif 0 < data['$pP-used'] < 10 and data.get('growth-used', 1) < 1.0:
		data['flag'] = "PARTOUT"
	else:
		data['flag'] = "??"

	return data

#============================
#============================
def make_timestamp():
	datestamp = time.strftime("%y%b%d").lower()
	hourstamp = string.ascii_lowercase[(time.localtime()[3])%26]
	if hourstamp == "x":
		### SPIDER does not like x's
		hourstamp = "z"
	timestamp = datestamp+hourstamp
	return timestamp

#============================
#============================
def make_big_timestamp():
	datestamp = time.strftime("%y%b%d").lower()
	hourstamp = string.ascii_lowercase[(time.localtime()[3])%26]
	if hourstamp == "x":
		### SPIDER does not like x's
		hourstamp = "z"
	#mins = time.localtime()[3]*12 + time.localtime()[4]
	#minstamp = string.lowercase[mins%26]
	minstamp = "%02d"%(time.localtime()[4])
	timestamp = datestamp+hourstamp+minstamp
	return timestamp

#============================
#============================
def read_setIDs_from_file(setIDFile, remove_dups=False):
	if not os.path.isfile(setIDFile):
		return None
	setIDs = []
	f = open(setIDFile, "r")
	for line in f:
		sline = line.strip()
		if len(sline) < 2:
			continue
		if '\t' in sline:
			bits = sline.split('\t')
			sline = bits[0].strip()
		if sline.startswith('#'):
			continue
		elif re.search(r'^[0-9]+$', sline):
			legoID = int(sline)
			setID = '{0}-1'.format(legoID)
		elif re.search(r'^[0-9]+\-[0-9]+$', sline):
			setID = sline
		else:
			print("??? - '{0}'".format(sline))
			time.sleep(2)
			continue
		setIDs.append(setID)
	f.close()
	### remove duplicates
	if remove_dups is True:
		setIDs = list(set(setIDs))
	setIDs.sort()
	print("Found {0} set IDs to process".format(len(setIDs)))
	return setIDs

#============================
#============================
def processSetID(setID):
	if setID is None:
		return None
	if isinstance(setID, int):
		if 1000 < setID < 99999:
			setID = '{0}-1'.format(setID)
			return setID
		print("?setID?? - '{0}'".format(setID))
		return None
	if not isinstance(setID, str):
		print("?setID?? - '{0}'".format(setID))
		return None
	if ' ' in setID:
		return None
	if re.search(r'^[A-Za-z]+$', setID):
		return None
	if re.search(r'^[0-9]{4,5}-[0-9]+$', setID):
		#perfect
		return setID
	if re.search('^[0-9]{4,5}$', setID):
		setID = int(setID)
		if 1000 < setID < 99999:
			setID = '{0}-1'.format(setID)
			return setID
		print("?setID?? - '{0}'".format(setID))
		return None
	print("?setID?? - '{0}'".format(setID))
	return None

#============================
#============================
def read_minifigIDpairs_from_file(minifigIDFile: str, remove_dups: bool = False) -> list:
	"""
	Reads minifigure ID pairs from a file, with optional duplicate removal.

	Args:
		minifigIDFile (str): The file containing minifigure IDs.
		remove_dups (bool): Flag to indicate whether duplicates should be removed.

	Returns:
		list[tuple[str, str]]: List of minifigure ID and set ID pairs.
	"""
	if not os.path.isfile(minifigIDFile):
		return None

	minifigIDs = []
	pattern = r'^[a-zA-Z0-9]{2,}[0-9]{2,4}(?:[a-zA-Z]+)?[0-9]*$'

	with open(minifigIDFile, "r") as f:
		for line in f:
			sline = line.strip()
			if len(sline) < 2 or sline.startswith('#'):
				continue

			if '\t' in sline:
				bits = sline.split('\t')
			elif ',' in sline:
				bits = sline.split(',')
			else:
				bits = [sline, None]

			minifigID = bits[0].strip()
			setID = bits[1].strip() if bits[1] else None

			if not re.search(pattern, minifigID):
				print(f"?minifigID?? - '{minifigID}'")
				time.sleep(2)
				continue

			setID = processSetID(setID)
			minifigIDs.append((minifigID, setID))

	if remove_dups:
		minifigIDs = list(set(minifigIDs))

	minifigIDs.sort()
	print(f"Found {len(minifigIDs)} minifig ID pairs to process")
	return minifigIDs

	### remove duplicates
	if remove_dups is True:
		minifigIDs = list(set(minifigIDs))

	minifigIDs.sort()
	print("Found {0} minifig ID pairs to process".format(len(minifigIDs)))
	return minifigIDs
