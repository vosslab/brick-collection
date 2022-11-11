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
		self.start()

	#============================
	#============================
	def _get_set(self, set_number):
		time.sleep(random.random())
		self.api_calls += 1
		response = brickse.lego.get_set(set_number=set_number, extended_data=False)
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
		if self.api_daily_limit_exceeded is True:
			return None
		set_data = self._get_set(setID)
		if set_data is None:
			return None
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
					legoID, int(msrp)/100.))
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
