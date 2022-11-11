#!/usr/bin/env python3

import os
import sys
import time
import copy
import string

import libbrick
import rebrick_wrapper
import brickset_wrapper
import bricklink_wrapper

#============================
#============================
def getAllData(setID, rbw, bsw, blw):
	data = rbw.getSetDataDirect(setID)
	bsw_data = bsw.getSetDataDirect(setID)
	if bsw_data is not None:
		data |= bsw_data
	data |= blw.getSetDataDirect(setID)
	data |= blw.getSetDataDirect(setID)
	data |= blw.getSetPriceData(setID)
	data['msrp'] = bsw.getSetMSRP(setID)
	#print(data)

	data = libbrick.flatten_dict(data)
	data['$pP-retail'] = round(data['msrp']/data['num_parts'],1)
	data['$pP-used'] = round(data['used_median_sale_price']/data['num_parts'],1)
	data['$pP-new'] = round(data['new_median_sale_price']/data['num_parts'],1)
	data['growth-used'] = round(data['used_median_sale_price']/data['msrp'],1)
	data['growth-new'] = round(data['new_median_sale_price']/data['msrp'],1)

	if data['$pP-used'] > 10 and data['growth-used'] > 1.5:
		data['flag'] = "KEEP"
	elif data['year'] >= 2019:
		data['flag'] = "wait"
	elif 0 < data['$pP-used'] < 10 and data['growth-used'] < 1.0:
		data['flag'] = "PARTOUT"
	else:
		data['flag'] = "??"

	return data

#============================
#============================
if __name__ == '__main__':
	rbw = rebrick_wrapper.Rebrick()
	bsw = brickset_wrapper.BrickSet()
	blw = bricklink_wrapper.BrickLink()

	if len(sys.argv) < 2:
		print("usage: ./gimmeSetData.py <csv txt file with lego IDs>")
		sys.exit(1)
	setIDfile = sys.argv[1]
	if not os.path.isfile(setIDfile):
		print("usage: ./gimmeSetData.py <csv txt file with lego IDs>")
		sys.exit(1)

	#============================
	#============================
	setIDs = libbrick.read_setIDs_from_file(setIDfile)

	#============================
	#============================
	timestamp = libbrick.make_timestamp()
	csvfile = "set_data-gimme-{0}.csv".format(timestamp)

	#============================
	#============================

	line = 0
	data_tree = []
	allkeys = []
	line = 0
	for itemID in setIDs:
		line += 1
		sys.stderr.write(".")
		data = getAllData(itemID, rbw, bsw, blw)
		if data is None:
			continue
		data_tree.append(data)
		allkeys += data.keys()
		allkeys = list(set(allkeys))
		if line % 100 == 0:
			rbw.save_cache()
			bsw.save_cache()
			blw.save_cache()

	#random.shuffle(data_tree)
	rbw.close()
	bsw.close()
	blw.close()

	#============================
	#============================

	allkeys = sorted(allkeys, key=str.lower)
	f = open(csvfile, "w")
	for key in allkeys:
		if key.startswith('extended'):
			continue
		f.write("{0}\t".format(key.lower()))
	f.write("\n")
	for data in data_tree:
		set_line = ''
		for key in allkeys:
			if key.startswith('extended'):
				continue
			value = data.get(key)
			if value is not None:
				value = str(value).strip()
				value = value.replace('\t', ' ')
				value = value.replace('\n', ' ')
				value = value.replace(',', ' ')
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

	#============================
	#============================

	f.close()
	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(line, csvfile)))

	print(("open %s"%(csvfile)))
