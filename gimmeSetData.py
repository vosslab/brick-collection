#!/usr/bin/env python3

import os
import sys
import time
import copy
import string

import rebrick_wrapper
import brickset_wrapper
import bricklink_wrapper

from collections.abc import MutableMapping

def _flatten_dict_gen(d, parent_key, sep):
	for k, v in d.items():
		new_key = parent_key + sep + k if parent_key else k
		if isinstance(v, MutableMapping):
			yield from flatten_dict(v, new_key, sep=sep).items()
		else:
			yield new_key, v

def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str = '.'):
	return dict(_flatten_dict_gen(d, parent_key, sep))


#============================
#============================
def makeTimestamp():
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
if __name__ == '__main__':
	rbw = rebrick_wrapper.Rebrick()
	bsw = brickset_wrapper.BrickSet()
	blw = bricklink_wrapper.BrickLink()

	if len(sys.argv) < 2:
		print("usage: ./gimmeSetData.py <csv txt file with lego IDs>")
		sys.exit(1)
	legoidFile = sys.argv[1]
	if not os.path.isfile(legoidFile):
		print("usage: ./gimmeSetData.py <csv txt file with lego IDs>")
		sys.exit(1)

	#============================
	#============================
	legoIDs = []
	f = open(legoidFile, "r")
	for line in f:
		sline = line.strip()
		try:
			legoID = int(sline)
		except ValueError:
			continue
		legoIDs.append(legoID)
	f.close()
	legoIds = list(set(legoIDs))
	legoIDs.sort()
	print("Found {0} Lego IDs to process".format(len(legoIDs)))
	#random.shuffle(legoIDs)

	#============================
	#============================
	timestamp = makeTimestamp()
	csvfile = "set_data-gimme-{0}.csv".format(timestamp)

	#============================
	#============================
	f = open(csvfile, "w")
	line = 0
	for itemID in legoIDs:
		line += 1
		sys.stderr.write(".")
		#print(legoID)
		if blw._check_lego_ID(itemID) is True:
			setID = '{0}-1'.format(itemID)
		elif '-' in itemID:
			setID = itemID
		else:
			print("UNKNOWN ID: "+itemID)
			continue
		legoID = int(setID.split('-')[0])
		data = rbw.getSetDataDirect(setID)
		bsw_data = bsw.getSetDataDirect(setID)
		if bsw_data is not None:
			data |= bsw_data
		data |= blw.getSetDataDirect(setID)
		data |= blw.getSetDataDirect(setID)
		data |= blw.getSetPriceData(legoID)
		data['msrp'] = bsw.getSetMSRP(legoID)
		#print(data)
		if line % 25 == 0:
			rbw.save_cache()
			bsw.save_cache()
			blw.save_cache()
		data = flatten_dict(data)
		if line == 1:
			allkeys = list(data.keys())
			allkeys.sort()
			print(', '.join(allkeys))
			for key in allkeys:
				f.write("%s\t"%(str(key)))
			f.write("\n")
		set_line = ''
		for key in allkeys:
			value = data.get(key)
			if value is not None:
				value = str(value).strip()
				value = value.replace('\t', ' ')
				value = value.replace('\n', ' ')
				while '  ' in value:
					value = value.replace('  ', ' ')
				if len(value) > 100:
					value = value[:100]
				if isinstance(value, dict):
					print('not flat')
					sys.exit(1)
				else:
					set_line += "{0}\t".format(value)
			else:
				set_line += "\t"
		f.write(set_line+"\n")
	f.close()
	rbw.close()
	bsw.close()
	blw.close()
	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(line, csvfile)))

	print(("open %s"%(csvfile)))
