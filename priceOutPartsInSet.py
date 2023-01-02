#!/usr/bin/env python3

import os
import sys
import argparse

import libbrick
import bricklink_wrapper

#============================
#============================
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Find Price for All Parts in a Set')
	parser.add_argument('-l', '--legoid', dest='legoid', metavar='#', type=int,
		help='an integer for the Lego ID, e.g. 11011')
	parser.add_argument('-s', '--setid', dest='setid', metavar='#-1', type=int,
		help='a string for the Set ID, e.g. 11011-1')

	args = parser.parse_args()

	if args.setid is not None:
		setID = args.setid
	elif args.legoid is not None:
		setID = '{0:d}-1'.format(args.legoid)
	else:
		parser.print_help()
		sys.exit(1)

	BLW = bricklink_wrapper.BrickLink()
	sys.stderr.write(".")
	set_data = BLW.getSetData(setID)
	parts_tree = BLW.getPartsFromSet(setID)

	print('\nFound {0} unique parts in set {1} {2}'.format(len(parts_tree), setID, set_data['name']))

	timestamp = libbrick.make_timestamp()
	csvfile = "part_data-bricklink-{0}.csv".format(timestamp)
	f = open(csvfile, "w")
	line = 0
	#print(data)
	allkeys = None
	for part_dict in parts_tree:
		line += 1
		print("\nITEM {0} of {1}".format(line, len(parts_tree)))
		entries = part_dict['entries']
		if len(entries) > 1:
			print(entries)
			print('too many entries')
			sys.exit(1)
		part_data_plus = entries[0]
		part_data = part_data_plus['item']
		print(part_data_plus)
		partID = part_data['no']
		colorID = part_data_plus['color_id']
		price_data = BLW.getPartPriceData(partID, colorID)
		print(price_data)
		data = {}
		data.update(part_data_plus)
		data.update(part_data)
		data.update(price_data)
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
			if isinstance(value, int):
				f.write("{0:d}\t".format(value))
			elif isinstance(value, float):
				f.write("{0:.3f}\t".format(value))
			elif isinstance(value, str):
				if len(value) > 100:
					f.write("{0}\t".format(value[:100]))
				else:
					f.write("{0}\t".format(value))
			else:
				f.write("\t")
		f.write("\n")
		#if line > 10:

	f.close()
	BLW.close()
	print('open '+csvfile)
