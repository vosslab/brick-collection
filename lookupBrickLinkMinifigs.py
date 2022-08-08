#!/usr/bin/env python

import os
import sys
import html
import json
import time
import random
import string
import bricklink_wrapper

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
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)
	legoidFile = sys.argv[1]
	if not os.path.isfile(legoidFile):
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)

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

	timestamp = makeTimestamp()
	csvfile = "bricklink-minifig_data-{0}.csv".format(timestamp)
	f = open(csvfile, "w")
	line = 0
	BLwrap = bricklink_wrapper.BrickLink()

	for legoID in legoIDs:
		
		sys.stderr.write(".")
		#print(legoID)
		set_data = BLwrap.getSetData(legoID)
		minifig_set_tree = BLwrap.getMinifigsFromSet(legoID)
		for minifig_data in minifig_set_tree:
			line += 1
			if line == 1:
				allkeys = list(minifig_data.keys())
				allkeys.sort()
				print(', '.join(allkeys))
				for key in allkeys:
					f.write("%s\t"%(str(key)))
				f.write("\n")
			for key in allkeys:
				try:
					value = minifig_data[key]
					if isinstance(value, str):
						value = value.replace(',', ' ')
						value = value.replace('  ', ' ')
						if '&' in value:
							value = html.unescape(value)
					f.write("%s\t"%(str(value)))
				except KeyError:
					print("missing key: "+key)
					f.write("\t")
			f.write("\n")
			if line % 50 == 0:
				BLwrap.save_cache()
		
	f.close()
	BLwrap.close()
	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(line, csvfile)))

	print(("open %s"%(csvfile)))
