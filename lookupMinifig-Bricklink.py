#!/usr/bin/env python3

import os
import sys
import html

import libbrick
import bricklink_wrapper

#============================
#============================
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)
	minifigIDFile = sys.argv[1]
	if not os.path.isfile(minifigIDFile):
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)

	minifigIDs = libbrick.read_minifigIDs_from_file(minifigIDFile)

	timestamp = libbrick.make_timestamp()
	csvfile = "minifig_data-bricklink-{0}.csv".format(timestamp)

	f = open(csvfile, "w")
	BLwrap = bricklink_wrapper.BrickLink()
	line = 0
	for minifigID in minifigIDs:
		line += 1
		sys.stderr.write(".")
		minifig_data = BLwrap.getMinifigData(minifigID)
		category_name = BLwrap.getCategoryNameFromMinifigID(minifigID)
		minifig_data['category_name'] = category_name
		price_data = BLwrap.getMinifigsPriceData(minifigID)
		total_data = {**minifig_data, **price_data}
		total_data['minifig_id'] = minifigID
		if line == 1:
			allkeys = list(total_data.keys())
			#allkeys.sort()
			print(', '.join(allkeys))
			for key in allkeys:
				f.write("%s\t"%(str(key.lower())))
			f.write("\n")
		for key in allkeys:
			try:
				value = total_data[key]
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
