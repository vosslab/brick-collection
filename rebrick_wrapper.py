#!/usr/bin/env python3

import sys
import time
import yaml
import json
import random
import rebrick
import wrapper_base

class Rebrick(wrapper_base.BaseWrapperClass):
	#============================
	#============================
	def __init__(self):
		self.debug = True

		api_dict = yaml.safe_load(open('rebrick_api_key.yml', 'r'))
		api_key = api_dict['api_key']
		rebrick.init(api_key)
		#Usage: init(API_KEY) or init(API_KEY, USER_TOKEN) or init(API_KEY, username, password)

		self.data_caches = {
			'rebrick_theme_cache': 			'yml',
			'rebrick_set_cache': 			'json',
			'rebrick_part_cache': 			'json',
			'rebrick_minifig_cache': 		'json',
			'rebrick_minifig_set_cache': 	'json',
		}
		self.api_calls = 0
		self.start()

	#============================
	#============================
	def getThemeName(self, themeID, verbose=True):
		theme_name = self.rebrick_theme_cache.get(themeID)
		###################
		if theme_name is not None:
			return theme_name
		###################
		time.sleep(random.random())
		response = rebrick.lego.get_theme(themeID)
		sys.stderr.write('#')
		self.api_calls += 1
		theme_data = json.loads(response.read())
		#print(theme_data)
		if theme_data.get('parent_id') is not None:
			parent_name = self.getThemeName(theme_data.get('parent_id'))
			if not theme_data['name'].startswith(parent_name):
				theme_name = parent_name + ' ' + theme_data['name']
				theme_data['name'] = theme_name
			else:
				theme_name = theme_data['name']
		else:
			theme_name = theme_data['name']
		self.rebrick_theme_cache[themeID] = theme_name
		#print(theme_name)
		return theme_name

	#============================
	#============================
	def getSetData(self, setID, verbose=True):
		self._check_set_ID(setID)
		###################
		set_data = self.rebrick_set_cache.get(setID)
		if self._check_if_data_valid(set_data) is True:
			if verbose is True:
				print('SET {0} -- {1} ({2}) -- from cache'.format(
					set_data.get('set_num'), set_data.get('name'), set_data.get('year'),))
			# update connected data
			set_data['theme_name'] = self.getThemeName(set_data['theme_id'])
			self.rebrick_set_cache[setID] = set_data
			return set_data
		###################
		time.sleep(random.random())
		response = rebrick.lego.get_set(setID)
		sys.stderr.write('#')
		self.api_calls += 1
		set_data = json.loads(response.read())
		set_data['theme_name'] = self.getThemeName(set_data['theme_id'])
		print('SET {0} -- {1} ({2}) -- from Rebrick website'.format(
			set_data.get('set_num'), set_data.get('name'), set_data.get('year'),))
		set_data['time'] = int(time.time())
		set_data['set_id'] = setID
		self.rebrick_set_cache[setID] = set_data
		if self.api_calls % 25 == 0:
			self.save_cache()
		return set_data

	#============================
	#============================
	def getSetDataDirect(self, setID, verbose=True):
		return self.getSetData(setID, verbose)

	#============================
	#============================
	def getPartsFromSet(self, setID, verbose=True):
		self._check_set_ID(setID)
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return subsets_tree

	#============================
	#============================
	def getSetPriceDetails(self, setID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		self._check_set_ID(setID)
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return price_data

	#============================
	#============================
	def getMinifigPriceDetails(self, minifigID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return price_data

	#============================
	#============================
	def getMinifigsPrice(self, minifigID):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return avg_price, sales

	#============================
	#============================
	def getMinifigsFromSet(self, setID, verbose=True):
		self._check_set_ID(setID)
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return minifig_set_tree

	#============================
	#============================
	def getMinifigData(self, minifigID, verbose=True):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return minifig_data

	#============================
	#============================
	def getPartData(self, partID, verbose=True):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return part_data


if __name__ == "__main__":
	rb = Rebrick()
	s = rb.getSetData(75155)
	#import pprint
	#pprint.pprint(s)
	print(s.keys())
	print("num_parts", s['num_parts'])
	rb.close()
