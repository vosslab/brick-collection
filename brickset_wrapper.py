#!/usr/bin/env python3

import os
import sys
import time
import yaml
import json
import random
import brickse
import wrapper_base

class BrickSet(wrapper_base.BaseWrapperClass):
	#============================
	#============================
	def __init__(self):
		self.debug = True
		key_file_name = 'brickset_api_private.yml'
		local_key_path = os.path.join(os.path.dirname(__file__), key_file_name)
		self.api_data = None  # Ensure it's defined
		# Check in the current working directory
		if os.path.exists(key_file_name):
			with open(key_file_name, 'r') as f:
				self.api_data = yaml.safe_load(f)
		# Check in the script's directory
		elif os.path.exists(local_key_path):
			with open(local_key_path, 'r') as f:
				self.api_data = yaml.safe_load(f)
		# If no valid file was found, exit with an error
		if self.api_data is None:
			print("Error: API key file not found.")
			exit(1)
		self.api_key = self.api_data['web_services_key_2']
		#print(self.web_services_key)
		#self.user_token = ''
		brickse.init(self.api_key)
		self.api_daily_limit_exceeded = False

		self.data_caches = {
			'brickset_category_cache': 		'yml',
			'brickset_msrp_cache': 			'yml',

			'brickset_set_cache': 			'json',
			'brickset_part_cache': 			'json',
			'brickset_minifig_cache': 		'json',
			'brickset_minifig_set_cache': 	'json',
		}
		self.api_calls = 0
		self.start()

	#============================
	#============================
	def _get_set(self, set_number):
		time.sleep(random.random())
		self.api_calls += 1
		response = brickse.lego.get_set(set_number=set_number, extended_data=False)
		sys.stderr.write('#')
		data = json.loads(response.read())
		if data['status'] != "success":
			self.save_cache()
			if data.get('message') == 'API limit exceeded':
				print('BrickSet API limit exceeded')
				print("{0} api calls were made".format(self.api_calls))
				for i in range(9):
					time.sleep(random.random())
					print(".")
				self.api_daily_limit_exceeded = True
				return None
			print("STATUS ERROR", data['status'])
			print(list(data.keys()))
			import pprint
			try:
				pprint.pprint(data['sets'][0])
			except KeyError:
				pprint.pprint(data)
			sys.exit(1)
		if data['matches'] != 1:
			print("MATCHES ERROR", data['matches'])
			print(list(data.keys()))
			import pprint
			pprint.pprint(data['sets'][0])
			sys.exit(1)
		set_data = data['sets'][0]
		if self.debug is True:
			print('SET {0} -- {1} ({2}) -- from BrickSet website'.format(
				set_data.get('number'), set_data.get('name'), set_data.get('year'),))
		set_data['time'] = int(time.time())
		return set_data

	#============================
	#============================
	def getSetData(self, setID, verbose=True):
		self._check_set_ID(setID)
		set_data = self.getSetDataDirect(setID)
		return set_data

	#============================
	#============================
	def getSetDataDirect(self, setID, verbose=True):
		""" get the set data from BrickSet using a setID with hyphen, e.g. 71515-2 """
		self._check_set_ID(setID)
		###################
		set_data = self.brickset_set_cache.get(setID)
		if self._check_if_data_valid(set_data) is True:
			if verbose is True:
				print('SET {0} -- {1} ({2}) -- from cache'.format(
					set_data.get('number'), set_data.get('name'), set_data.get('year'),))
			# update connected data
			#set_data['category_name'] = self.getCategoryName(set_data['category_id'])
			self.brickset_set_cache[setID] = set_data
			return set_data
		###################
		if self.api_daily_limit_exceeded is True:
			return None
		set_data = self._get_set(setID)
		if set_data is None:
			return None
		self.brickset_set_cache[setID] = set_data
		return set_data

	#============================
	#============================
	def getSetMSRP(self, setID, region='US', verbose=True):
		self._check_set_ID(setID)
		###################
		msrp = self.brickset_msrp_cache.get(setID)
		if msrp == 0 or msrp is None:
			set_data = self.brickset_set_cache.get(setID)
			if set_data is not None:
				if 'polybag' in set_data['name']:
					msrp = 499
					print("... polybag")
					time.sleep(random.random())
					time.sleep(random.random())
					self.brickset_msrp_cache[setID] = msrp
					return msrp
				else:
					print(set_data['name'])
		if msrp == 0 and random.random() < 0.01:
			# 0 means it was not found, 10% chance to check again
			print("... check for MSRP again")
			time.sleep(random.random())
			time.sleep(random.random())
			pass
		elif msrp is not None:
			if verbose is True:
				print('SET {0} -- MSRP ${1:.2f} -- from cache'.format(
					setID, int(msrp)/100.))
			return msrp
		###################
		if self.api_daily_limit_exceeded is True:
			return None
		set_data = self._get_set(setID)
		if set_data is None:
			return None
		legocom = set_data.get('LEGOCom')
		region = legocom.get(region)
		if region is None:
			#print(', '.join(legocom.keys()))
			self.brickset_msrp_cache[setID] = 0
			return None
		price = region.get('retailPrice')
		if price is None:
			#print(', '.join(legocom.keys()))
			#print(type(region), len(region.keys()))
			#print(', '.join(region.keys()))
			self.brickset_msrp_cache[setID] = 0
			return None
		msrp = price
		#save value as integer in cents
		msrp = int(round(msrp*100))
		self.brickset_msrp_cache[setID] = msrp
		return msrp

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
	bs = BrickSet()
	s = bs.getSetData(75155)
	#import pprint
	#pprint.pprint(s)
	msrp = bs.getSetMSRP(75155)
	print("MSRP", msrp)
	bs.close()
