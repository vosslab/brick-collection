#!/usr/bin/env python3

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
		self.api_data = yaml.safe_load(open('brickset_api_private.yml', 'r'))
		self.web_services_key = self.api_data['web_services_key_2']
		#self.cache_format = 'yml'
		self.cache_format = 'json'
		#print(self.web_services_key)
		#self.user_token = ''
		brickse.init(self.web_services_key)

		self.load_cache()
		self.expire_time = 14 * 24 * 3600 # 14 days, in seconds
		self.data_refresh_cutoff = 0.01 # 1% of the data is refreshed
		self.api_calls = 0
		self.api_log = []

		self.data_caches = {
			'brickset_category_cache': 		'yaml',
			'brickset_msrp_cache': 			'yaml',

			'brickset_set_cache': 			'json',
			'brickset_part_cache': 			'json',
			'brickset_minifig_cache': 		'json',
			'brickset_minifig_set_cache': 	'json',
		}
		self.start()

	#============================
	#============================
	def _get_set(self, set_number):
		time.sleep(random.random())
		response = brickse.lego.get_set(set_number=set_number, extended_data=False)
		data = json.loads(response.read())
		if data['status'] != "success":
			print("STATUS ERROR", data['status'])
			print(list(data.keys()))
			import pprint
			pprint.pprint(data['sets'][0])
			sys.exit(1)
		if data['matches'] != 1:
			print("MATCHES ERROR", data['matches'])
			print(list(data.keys()))
			import pprint
			pprint.pprint(data['sets'][0])
			sys.exit(1)
		set_data = data['sets'][0]
		set_data['time'] = int(time.time())
		return set_data

	#============================
	#============================
	def getSetData(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		setID = str(legoID) + "-1"
		set_data = self.getSetDataDirect(setID)
		return set_data

	#============================
	#============================
	def getSetDataDirect(self, setID, verbose=True):
		""" get the set data from BrickSet using a setID with hyphen, e.g. 71515-2 """
		legoID = int(setID.split('-')[0])
		self._check_lego_ID(legoID)
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
		set_data = self._get_set(setID)
		set_data['set_num'] = legoID
		self.brickset_set_cache[setID] = set_data
		return set_data

	#============================
	#============================
	def getSetMSRP(self, legoID, region='US', verbose=True):
		self._check_lego_ID(legoID)
		setID = str(legoID) + "-1"
		###################
		msrp = self.brickset_msrp_cache.get(setID)
		if msrp is not None:
			if verbose is True:
				print('SET {0} -- MSRP ${1:.2f} -- from cache'.format(
					legoID, int(msrp)/100.))
			return msrp
		###################
		set_data = self._get_set(setID)
		msrp = set_data['LEGOCom'][region]['retailPrice']
		#save value as integer in cents
		msrp = int(round(msrp*100))
		self.brickset_msrp_cache[setID] = msrp
		return set_data

	#============================
	#============================
	def getPartsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		#return subsets_tree

	#============================
	#============================
	def getSetPriceDetails(self, legoID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		self._check_lego_ID(legoID)
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
	def getMinifigsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
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
