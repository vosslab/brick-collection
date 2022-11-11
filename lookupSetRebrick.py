#!/usr/bin/env python3

import os
import re
import sys
import json
import time
import yaml
import random
import string
import rebrick_wrapper

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
		print("usage: ./lookupLego.py <txt file with lego IDs>")
		sys.exit(1)
	setIDFile = sys.argv[1]
	if not os.path.isfile(setIDFile):
		print("usage: ./lookupLego.py <txt file with lego IDs>")
		sys.exit(1)

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

	timestamp = makeTimestamp()
	csvfile = "set_data-rebrick-{0}.csv".format(timestamp)
	f = open(csvfile, "w")
	line = 0
	rbw = rebrick_wrapper.Rebrick()
	for setID in setIDs:
		line += 1
		sys.stderr.write(".")
		data = rbw.getSetData(setID)
		#print(data)
		if line == 1:
			allkeys = list(data.keys())
			allkeys.sort()
			print(', '.join(allkeys))
			for key in allkeys:
				f.write("%s\t"%(str(key)))
			f.write("\n")
		for key in allkeys:
			try:
				f.write("%s\t"%(str(data[key])))
			except KeyError:
				print("missing key: "+key)
				f.write("\t")
		f.write("\n")
	f.close()
	rbw.close()
	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(line, csvfile)))
	print(("open %s"%(csvfile)))
