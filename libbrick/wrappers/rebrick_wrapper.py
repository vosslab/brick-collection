#!/usr/bin/env python3

# Standard Library
import os
import sys
import json
import time
import random

# PIP3 modules
import yaml
import rebrick

# local repo modules
import libbrick.path_utils
import libbrick.wrappers.wrapper_base as wrapper_base

class Rebrick(wrapper_base.BaseWrapperClass):
	#============================
	#============================
	def __init__(self):
		self.debug = True
		key_file_name = 'rebrick_api_key.yml'
		local_key_path = os.path.join(os.path.dirname(__file__), key_file_name)
		git_root = libbrick.path_utils.get_git_root()
		api_dict = None  # Ensure it's defined
		key_paths = []
		if git_root is not None:
			key_paths.append(os.path.join(git_root, key_file_name))
		key_paths.append(key_file_name)
		key_paths.append(local_key_path)
		for key_path in key_paths:
			if os.path.exists(key_path):
				with open(key_path, 'r') as f:
					api_dict = yaml.safe_load(f)
				break
		# If no valid file was found, exit with an error
		if api_dict is None:
			print("Error: API key file not found.")
			exit(1)

		# Extract the API key
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
		try:
			response = rebrick.lego.get_set(setID)
		except:
			return None
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
