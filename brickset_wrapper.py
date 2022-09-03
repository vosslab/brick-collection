#!/usr/bin/env python3

import os
import sys
import time
import yaml
import json
import random
import brickse

class BrickSet(object):
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

	#============================
	#============================
	def load_cache(self):
		print('==== LOAD CACHE ====')
		self.data_caches = [
			'brickset_category_cache',
			'brickset_set_cache',
			'brickset_msrp_cache',
			'brickset_part_cache',
			'brickset_minifig_cache',
			'brickset_minifig_set_cache',
		]

		for cache_name in self.data_caches:
			file_name = 'CACHE/'+cache_name+'.'+self.cache_format
			if os.path.isfile(file_name):
				try:
					t0 = time.time()
					if self.cache_format == 'json':
						cache_data = json.load( open(file_name, 'r') )
					elif self.cache_format == 'yml':
						cache_data =  yaml.safe_load( open(file_name, 'r') )
					print('.. loaded {0} entires from {1} in {2:d} usec'.format(
						len(cache_data), file_name, int((time.time()-t0)*1e6)))
				except IOError:
					cache_data = {}
			else:
				cache_data = {}
			setattr(self, cache_name, cache_data)
		#print(getattr(self, 'bricklink_set_cache').keys())
		print('==== END CACHE ====')


	#============================
	#============================
	def close(self):
		self.save_cache()

	#============================
	#============================
	def save_cache(self):
		print('==== SAVE CACHE ====')
		if not os.path.isdir('CACHE'):
			os.mkdir('CACHE')
		for cache_name in self.data_caches:
			t0 = time.time()
			file_name = 'CACHE/'+cache_name+'.'+self.cache_format
			cache_data = getattr(self, cache_name)
			if len(cache_data) > 0:
				if self.cache_format == 'json':
					json.dump( cache_data, open( file_name, 'w') )
				elif self.cache_format == 'yml':
					yaml.dump( cache_data, open( file_name, 'w') )
				print('.. wrote {0} entires to {1} in {2:d} usec'.format(
					len(cache_data), file_name, int((time.time()-t0)*1e6)))
		print('==== END CACHE ====')

	#============================
	#============================
	def _check_lego_ID(self, legoID):
		""" check to make sure number is valid """
		if not isinstance(legoID, int):
			legoID = int(legoID)
		if legoID < 3000:
			print("Error: Lego set ID is too small: {0}".format(legoID))
			sys.exit(1)
		elif legoID > 99999:
			print("Error: Lego set ID is too big: {0}".format(legoID))
			sys.exit(1)
		return True

	#============================
	#============================
	def _check_if_data_valid(self, cache_data_dict):
		""" common function of data expiration """
		if cache_data_dict is None:
			return False
		###################
		if not isinstance(cache_data_dict, dict):
			print(cache_data_dict)
			print("WRONG CACHE type, must be dict!!!")
			print(type(cache_data_dict))
			return False
		if cache_data_dict.get('time') is None:
			return False
		###################
		if time.time() - int(cache_data_dict.get('time')) > self.expire_time:
			return False
		###################
		if random.random() < self.data_refresh_cutoff:
			# reset data to None, 10% of the time
			# keeps the data fresh
			return False
		###################
		return True

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
		return subsets_tree

	#============================
	#============================
	def getSetPriceDetails(self, legoID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		self._check_lego_ID(legoID)
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		return price_data

	#============================
	#============================
	def getMinifigPriceDetails(self, minifigID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		return price_data

	#============================
	#============================
	def getMinifigsPrice(self, minifigID):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		return avg_price, sales

	#============================
	#============================
	def getMinifigsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		return minifig_set_tree

	#============================
	#============================
	def getMinifigData(self, minifigID, verbose=True):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		return minifig_data

	#============================
	#============================
	def getPartData(self, partID, verbose=True):
		print("NOT IMPLEMENTED YET")
		sys.exit(1)
		return part_data


if __name__ == "__main__":
	bs = BrickSet()
	s = bs.getSetData(75155)
	#import pprint
	#pprint.pprint(s)
	msrp = bs.getSetMSRP(75155)
	print("MSRP", msrp)
	bs.close()
