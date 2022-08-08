#!/usr/bin/env python

import os
import sys
import json
import time
import yaml
import random
import string
import bricklink
import bricklink.api

api_data = yaml.safe_load(open('bricklink_api_private.yml', 'r'))
bricklink_api = bricklink.api.BrickLinkAPI(
  api_data['consumer_key'], api_data['consumer_secret'],
  api_data['token_value'], api_data['token_secret'])

try:
	bricklink_category_cache = yaml.safe_load( open( "CACHE/bricklink_category_cache.yml", "r" ) )
	print("loaded %d entires from bricklink_category_cache"%(len(bricklink_category_cache)))
except IOError:
	bricklink_category_cache = {}

try:
	bricklink_set_cache = yaml.safe_load( open( "CACHE/bricklink_set_cache.yml", "r" ) )
	print("loaded %d entires from bricklink_set_cache"%(len(bricklink_set_cache)))
except IOError:
	bricklink_set_cache = {}

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
def getCategoryName(categoryID):
	category_name = bricklink_category_cache.get(categoryID)
	if category_name is not None:
		return category_name
	time.sleep(random.random())
	status, headers, response = bricklink_api.get('categories/{0}'.format(categoryID))
	category_data = response['data']
	#print(category_data)
	if category_data.get('parent_id') is not None and category_data.get('parent_id') > 1:
		parent_name = getCategoryName(category_data.get('parent_id'))
		if not category_data['category_name'].startswith(parent_name):
			category_name = parent_name + ' ' + category_data['category_name']
			category_data['category_name'] = category_name
		else:
			category_name = category_data['category_name']
	else:
		category_name = category_data['category_name']
	bricklink_category_cache[categoryID] = category_name
	#print(category_name)
	return category_name

#============================
#============================
def getSetData(legoID):
	set_data = bricklink_set_cache.get(legoID)
	if set_data is not None:
		print('{0} -- {1} -- from cache'.format(set_data.get('set_num'), set_data.get('name'),))
		set_data['category_name'] = getCategoryName(set_data['category_id'])
		bricklink_set_cache[legoID] = set_data
		return set_data
	if legoID < 3000:
		print("Error: Lego set ID is too small: {0}".format(legoID))
		sys.exit(1)
	elif legoID > 99999:
		print("Error: Lego set ID is too big: {0}".format(legoID))
		sys.exit(1)
	time.sleep(random.random())
	status, headers, response = bricklink_api.get('items/set/{0}-1'.format(legoID))
	set_data = response['data']
	set_data['category_name'] = getCategoryName(set_data['category_id'])
	print('{0} -- {1} -- from BrickLink website'.format(set_data.get('no'), set_data.get('name'),))

	bricklink_set_cache[legoID] = set_data
	return set_data

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
	csvfile = "bricklink-legoid_data-{0}.csv".format(timestamp)
	f = open(csvfile, "w")
	line = 0
	for legoID in legoIDs:
		line += 1
		sys.stderr.write(".")
		#print(legoID)
		data = getSetData(legoID)
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
	sys.stderr.write("\n")
	print(("Wrote %d lines to %s"%(line, csvfile)))

	yaml.dump( bricklink_set_cache, open( "CACHE/bricklink_set_cache.yml", "w" ) )
	print("wrote %d entires to bricklink_set_cache"%(len(bricklink_set_cache)))
	yaml.dump( bricklink_category_cache, open( "CACHE/bricklink_category_cache.yml", "w" ) )
	print("wrote %d entires to bricklink_category_cache"%(len(bricklink_category_cache)))

	print(("open %s"%(csvfile)))
