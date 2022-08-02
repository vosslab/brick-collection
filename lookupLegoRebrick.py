#!/usr/bin/env python

import os
import sys
import json
import time
import yaml
import random
import string
import rebrick

api_dict = yaml.safe_load(open('rebrick_api_key.yml', 'r'))
api_key = api_dict['api_key']
rebrick.init(api_key)
#Usage: init(API_KEY) or init(API_KEY, USER_TOKEN) or init(API_KEY, username, password).

try:
	rebrick_theme_cache = yaml.safe_load( open( "rebrick_theme_cache.yml", "r" ) )
	print("loaded %d entires from rebrick_theme_cache"%(len(rebrick_theme_cache)))
except IOError:
	rebrick_theme_cache = {}
try:
	rebrick_set_cache = yaml.safe_load( open( "rebrick_set_cache.yml", "r" ) )
	print("loaded %d entires from rebrick_set_cache"%(len(rebrick_set_cache)))
except IOError:
	rebrick_set_cache = {}

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
def getThemeName(themeID):
	theme_name = rebrick_theme_cache.get(themeID)
	if theme_name is not None:
		return theme_name
	response = rebrick.lego.get_theme(themeID)
	theme_data = json.loads(response.read())
	#print(theme_data)
	if theme_data.get('parent_id') is not None:
		parent_name = getThemeName(theme_data.get('parent_id'))
		if not theme_data['name'].startswith(parent_name):
			theme_name = parent_name + ' ' + theme_data['name']
			theme_data['name'] = theme_name
		else:
			theme_name = theme_data['name']
	else:
		theme_name = theme_data['name']
	rebrick_theme_cache[themeID] = theme_name
	#print(theme_name)
	return theme_name

#============================
#============================
def getSetData(legoID):
	set_data = rebrick_set_cache.get(legoID)
	if set_data is not None:
		print('{0} -- {1} -- from cache'.format(set_data.get('set_num'), set_data.get('name'),))
		return set_data
	if legoID < 3000:
		print("Error: Lego set ID is too small: {0}".format(legoID))
		sys.exit(1)
	elif legoID > 99999:
		print("Error: Lego set ID is too big: {0}".format(legoID))
		sys.exit(1)
	time.sleep(random.random())
	response = rebrick.lego.get_set(legoID)
	set_data = json.loads(response.read())
	set_data['theme_name'] = getThemeName(set_data['theme_id'])
	print('{0} -- {1} -- from Rebrick website'.format(set_data.get('set_num'), set_data.get('name'),))

	rebrick_set_cache[legoID] = set_data
	return set_data

#============================
#============================
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <txt file with lego IDs>")
		sys.exit(1)
	legoidFile = sys.argv[1]
	if not os.path.isfile(legoidFile):
		print("usage: ./lookupLego.py <txt file with lego IDs>")
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
	csvfile = "rebrick_legoid_data_output-{0}.csv".format(timestamp)
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

	yaml.dump( rebrick_theme_cache, open( "rebrick_theme_cache.yml", "w" ) )
	print("wrote %d entires to rebrick_theme_cache"%(len(rebrick_theme_cache)))
	yaml.dump( rebrick_set_cache, open( "rebrick_set_cache.yml", "w" ) )
	print("wrote %d entires to rebrick_set_cache"%(len(rebrick_set_cache)))

	print(("open %s"%(csvfile)))

