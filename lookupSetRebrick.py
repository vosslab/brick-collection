#!/usr/bin/env python3

import os
import sys

import libbrick
import rebrick_wrapper

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

	setIDs = libbrick.read_setIDs_from_file(setIDFile)
	timestamp = libbrick.make_timestamp()

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
