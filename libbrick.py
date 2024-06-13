
import re
import os
import time
import string
from collections.abc import MutableMapping

#============================
#============================
def _flatten_dict_gen(d, parent_key, sep):
	for k, v in d.items():
		new_key = parent_key + sep + k if parent_key else k
		if isinstance(v, MutableMapping):
			yield from flatten_dict(v, new_key, sep=sep).items()
		else:
			yield new_key, v

#============================
#============================
def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.'):
	return dict(_flatten_dict_gen(d, parent_key, sep))

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
	pattern = r'^[a-zA-Z]{2,}[0-9]{2,4}(?:[a-zA-Z]+)?[0-9]*$'

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
