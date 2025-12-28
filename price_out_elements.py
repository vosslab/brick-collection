#!/usr/bin/env python3

import os
import sys
import time
import random
import argparse

import libbrick
import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

#============================
#============================
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Find Price for All Parts in a Set')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-c', '--csv', dest='csvfile', metavar='FILE', type=str,
		help='CSV file with list of elements')
	group.add_argument('-e', '--elementid', dest='elementid', metavar='#', type=int,
		help='an integer for the element ID, e.g. 6314891')

	args = parser.parse_args()


	if args.csvfile is not None and os.path.isfile(args.csvfile) is True:
		elementIDs = []
		f = open(args.csvfile, 'r')
		for line in f:
			sline = line.strip()
			if len(sline) < 4 or len(sline) > 7:
				continue
			if sline.startswith('#'):
				continue
			try:
				elementID = int(sline)
			except ValueError:
				continue
			elementIDs.append(elementID)
		print('Found {0} element IDs in file {1}'.format(len(elementIDs), args.csvfile))
	elif args.elementid is not None:
		elementIDs = [args.elementid, ]


	BLW = bricklink_wrapper.BrickLink()
	sys.stderr.write(".")
	timestamp = libbrick.make_timestamp()
	output_dir = libbrick.path_utils.get_output_dir()
	csvfile = os.path.join(output_dir, "element_price_data-bricklink-{0}.csv".format(timestamp))
	f = open(csvfile, "w")
	line = 0
	#print(data)
	allkeys = None
	for elementID in elementIDs:
		line += 1
		skip = False
		print("\nELEMENT {0} of {1}".format(line, len(elementIDs)))
		t0 = time.time()
		map_list = BLW.elementIDtoPartIDandColorID(elementID)
		if map_list is None or len(map_list) != 2:
			data = {
				'element id': elementID,
			}
		else:
			partID, colorID = map_list

			price_data = BLW.getPartPriceData(partID, colorID, min_qty=1, verbose=True)
			weighted_price = BLW.getWeightedAveragePrice(price_data, new_or_used='N')

			if time.time() - t0 > 0.1:
				time.sleep(random.random())

			url = 'https://www.bricklink.com/v2/catalog/catalogitem.page?P={0}#T=S&C={1}'.format(partID, colorID)
			data = {
				'element id': elementID,
				'BL part id': partID,
				'BL color id': colorID,
				'weighted price': weighted_price,
				'zBL url': url,
			}
		###
		#data.update(price_data)
		#sys.exit(1)
		if line == 1:
			allkeys = list(data.keys())
			allkeys.sort()
			print(', '.join(allkeys))
			for key in allkeys:
				f.write("%s\t"%(str(key)))
			f.write("\n")
		for key in allkeys:
			value = data.get(key)
			if value is None:
				print("missing key: "+key)
				f.write("\t")
			elif isinstance(value, int):
				f.write("{0:d}\t".format(value))
			elif isinstance(value, float):
				f.write("{0:.3f}\t".format(value))
			elif isinstance(value, str):
				value = value.replace(",", " ")
				value = value.replace("\t", " ")
				if len(value) > 70:
					f.write("{0}\t".format(value[:70]))
				else:
					f.write("{0}\t".format(value))
			else:
				print("skipping key: "+key)
				f.write("\t")
		f.write("\n")
		if line % 10 == 0:
			BLW.save_cache()

	f.close()
	BLW.close()
	print('open '+csvfile)
