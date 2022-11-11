
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
	#mins = time.localtime()[3]*12 + time.localtime()[4]
	#minstamp = string.lowercase[mins%26]
	minstamp = "%02d"%(time.localtime()[4])
	timestamp = datestamp+hourstamp+minstamp
	return timestamp

#============================
#============================
def read_setIDs_from_file(setIDFile):
	if not os.path.isfile(setIDFile):
		return None
	setIDs = []
	f = open(setIDFile, "r")
	for line in f:
		sline = line.strip()
		if sline.startswith('#'):
			continue
		elif re.search('^[0-9]+$', sline):
			legoID = int(sline)
			setID = '{0}-1'.format(legoID)
		elif re.search('^[0-9]+\-[0-9]+$', sline):
			setID = sline
		else:
			print("???", sline)
			continue
		setIDs.append(setID)
	f.close()
	setIDs = list(set(setIDs))
	setIDs.sort()
	print("Found {0} set IDs to process".format(len(setIDs)))
	return setIDs
