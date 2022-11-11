#!/usr/bin/env python3

import sys
import time
import yaml
import random
import statistics
import wrapper_base
import bricklink.api

class BrickLink(wrapper_base.BaseWrapperClass):
	#============================
	#============================
	def __init__(self):
		self.debug = True
		self.api_data = yaml.safe_load(open('bricklink_api_private.yml', 'r'))
		self.bricklink_api = bricklink.api.BrickLinkAPI(
		  self.api_data['consumer_key'], self.api_data['consumer_secret'],
		  self.api_data['token_value'], self.api_data['token_secret'])

		self.price_count = 0
		self.data_caches = {
			'bricklink_category_cache': 		'yml',
			'bricklink_price_cache': 			'yml',
			'bricklink_set_brick_weight_cache': 'yml',

			'bricklink_subset_cache': 			'json',
			'bricklink_minifig_cache': 			'json',
			'bricklink_minifig_set_cache': 		'json',
			'bricklink_part_cache': 			'json',
			'bricklink_set_cache': 				'json',
		}
		self.start()

	#============================
	#============================
	def _bricklink_get(self, url):
		""" common function for all API calls """
		#random sleep of 0-1 seconds to help server load
		time.sleep(random.random())
		status, headers, response = self.bricklink_api.get(url)
		self.api_calls += 1
		self.api_log.append(url)
		error_msg = False
		if ( response.get('data') is None
			 or len(response.get('data')) == 0):
			error_msg = True
		if error_msg is True:
			self.save_cache()
			print('URL', url)
			print("STATUS", status)
			print("HEADERS", headers)
			print("RESPONSE", response)
			sys.exit(1)
		data = response['data']
		if isinstance(data, dict):
			data['time'] = int(time.time())
		return data

	#============================
	#============================
	def getCategoryName(self, categoryID):
		""" get the category name from BrickLink """
		###################
		# expire does NOT apply to category names
		category_name = self.bricklink_category_cache.get(categoryID)
		if category_name is not None:
			return category_name
		###################
		category_data = self._bricklink_get('categories/{0}'.format(categoryID))
		###################
		#print(category_data)
		if category_data.get('parent_id') is not None and category_data.get('parent_id') > 1:
			parent_name = self.getCategoryName(category_data.get('parent_id'))
			if not category_data['category_name'].startswith(parent_name):
				category_name = parent_name + ' ' + category_data['category_name']
				category_data['category_name'] = category_name
			else:
				category_name = category_data['category_name']
		else:
			category_name = category_data['category_name']
		self.bricklink_category_cache[categoryID] = category_name
		#print(category_name)
		return category_name

	#============================
	#============================
	def getSetData(self, legoID, verbose=True):
		""" get the set data from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		setID = str(legoID) + '-1'
		set_data = self.getSetDataDirect(setID, verbose)
		return set_data

	#============================
	#============================
	def getSetDataDetails(self, legoID, verbose=True):
		""" get the set data from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		setID = str(legoID) + '-1'
		set_data = self.getSetDataDirect(setID, verbose)
		price_dict = self.getSetPriceData(legoID)
		return set_data

	#============================
	#============================
	def getSetDataDirect(self, setID, verbose=True):
		""" get the set data from BrickLink using a setID with hyphen, e.g. 71515-2 """
		legoID = int(setID.split('-')[0])
		self._check_lego_ID(legoID)
		###################
		set_data = self.bricklink_set_cache.get(setID)
		if self._check_if_data_valid(set_data) is True:
			if verbose is True:
				print('SET {0} -- {1} ({2}) -- from cache'.format(
					set_data.get('no'), set_data.get('name'), set_data.get('year_released'),))
			# update connected data
			set_data['category_name'] = self.getCategoryName(set_data['category_id'])
			set_data['set_num'] = legoID
			self.bricklink_set_cache[setID] = set_data
			return set_data
		###################
		set_data = self._bricklink_get('items/set/{0}'.format(setID))
		###################
		if verbose is True:
			print('SET {0} -- {1} ({2}) -- from BrickLink website'.format(
				set_data.get('no'), set_data.get('name'), set_data.get('year_released'),))
		set_data['category_name'] = self.getCategoryName(set_data['category_id'])
		set_data['set_num'] = legoID
		self.bricklink_set_cache[setID] = set_data
		return set_data

	#============================
	#============================
	def getPartsFromSet(self, legoID, verbose=True):
		""" get all the parts from a set from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		###################
		subsets_tree = self._bricklink_get('items/set/{0}-1/subsets'.format(legoID))
		###################
		if verbose is True:
			print('SET {0} -- {1} parts -- from BrickLink website'.format(legoID, len(subsets_tree)))
		if self.debug is True:
			pass
			#self.bricklink_subsets_cache[legoID] = subsets_tree
		return subsets_tree

	#============================
	#============================
	def getSetBrickWeight(self, legoID, verbose=True):
		""" custom function to add up the weight of all the parts in a set """
		self._check_lego_ID(legoID)
		set_data = self.getSetData(legoID, verbose=False)
		###################
		string_weight = self.bricklink_set_brick_weight_cache.get(legoID)
		if string_weight is not None:
			if verbose is True:
				print('SET {0} -- {1} grams -- from set data'.format(legoID, set_data['weight']))
				print('SET {0} -- {1} grams -- from cache'.format(legoID, string_weight))
			return string_weight
		###################
		subsets_tree = self.getPartsFromSet(legoID, verbose=False)
		total_weight = 0
		for part in subsets_tree:
			for entry in part['entries']:
				item = entry['item']
				if item['type'] == 'MINIFIG':
					continue
				if item['type'] == 'GEAR':
					print(item['type'], item['name'])
					continue
				if item['type'] != 'PART':
					self.save_cache()
					print(item)
					print(item['type'])
					sys.exit(1)
				item_plus = self.getPartData(item['no'], verbose=False)
				weight = float(item_plus['weight'])
				qty = int(entry['quantity'])
				if verbose is True:
					print("{0:d} items weighing {1:.3f} grams".format(qty, weight))
				item_weight = (weight * qty)
				#print(item_weight)
				total_weight += item_weight
		string_weight = '{0:.3f}'.format(total_weight)
		if verbose is True:
			print('SET {0} -- {1} grams -- from set data'.format(legoID, set_data['weight']))
			print('SET {0} -- {1} grams -- from BrickLink website'.format(legoID, string_weight))
		self.bricklink_set_brick_weight_cache[legoID] = string_weight
		return string_weight

	#============================
	#============================
	def _lookUpPriceDataCache(self, item_id, verbose=True):
		""" common function for looking price data from cache """
		###################
		price_data = self.bricklink_price_cache.get(item_id)
		if self._check_if_data_valid(price_data) is True:
			if verbose is True:
				print('PRICE {0} -- ${1:.2f} -- ${2:.2f} -- ${3:.2f} -- ${4:.2f} -- from cache'.format(
					price_data.get('item_id'),
					float(price_data.get( 'new_median_sale_price'))/100.,
					float(price_data.get('used_median_sale_price'))/100.,
					float(price_data.get( 'new_median_list_price'))/100.,
					float(price_data.get('used_median_list_price'))/100.,
				))
			return price_data
		###################
		#print('price_data=', price_data)
		return None

	#============================
	#============================
	def _compilePriceData(self, item_id, new_price_sale_details, used_price_sale_details,
			new_price_list_details, used_price_list_details, verbose=True):
		###################
		new_avg_sale_price 	= int(float(new_price_sale_details['avg_price'])*100)
		new_sale_qty 		= int(new_price_sale_details['total_quantity'])
		used_avg_sale_price = int(float(used_price_sale_details['avg_price'])*100)
		used_sale_qty 		= int(used_price_sale_details['total_quantity'])
		new_avg_list_price 	= int(float(new_price_list_details['avg_price'])*100)
		new_list_qty 		= int(new_price_list_details['total_quantity'])
		used_avg_list_price = int(float(used_price_list_details['avg_price'])*100)
		used_list_qty 		= int(used_price_list_details['total_quantity'])
		###################
		# New Sales
		if new_sale_qty >= 1:
			new_sale_prices = []
			for item in new_price_sale_details['price_detail']:
				new_sale_prices.append(int(float(item['unit_price'])*100))
			new_median_sale_price = int(statistics.median(new_sale_prices))
			del new_sale_prices
		else:
			new_median_sale_price = -1
		###################
		# Used Sales
		if used_sale_qty >= 1:
			used_sale_prices = []
			for item in used_price_sale_details['price_detail']:
				used_sale_prices.append(int(float(item['unit_price'])*100))
			used_median_sale_price = int(statistics.median(used_sale_prices))
			del used_sale_prices
		else:
			used_median_sale_price = -1
		###################
		# New Sales
		if new_list_qty >= 1:
			new_list_prices = []
			for item in new_price_list_details['price_detail']:
				new_list_prices.append(int(float(item['unit_price'])*100))
			new_median_list_price = int(statistics.median(new_list_prices))
			del new_list_prices
		else:
			new_median_list_price = -1
		###################
		# Used Sales
		if used_list_qty >= 1:
			used_list_prices = []
			for item in used_price_list_details['price_detail']:
				used_list_prices.append(int(float(item['unit_price'])*100))
			used_median_list_price = int(statistics.median(used_list_prices))
			del used_list_prices
		else:
			used_median_list_price = -1
		###################
		price_data = {
			'item_id':					item_id,
			##=========
			'new_avg_sale_price': 		new_avg_sale_price,
			'new_median_sale_price': 	new_median_sale_price,
			'new_sale_qty': 			new_sale_qty,
			##=========
			'used_avg_sale_price': 	used_avg_sale_price,
			'used_median_sale_price': 	used_median_sale_price,
			'used_sale_qty': 			used_sale_qty,
			##=========
			'new_avg_list_price': 		new_avg_list_price,
			'new_median_list_price': 	new_median_list_price,
			'new_list_qty': 			new_list_qty,
			##=========
			'used_avg_list_price': 		used_avg_list_price,
			'used_median_list_price': 	used_median_list_price,
			'used_list_qty': 			used_list_qty,
			##=========
			'time':					int(time.time()),
		}
		if verbose is True:
			print('PRICE {0} -- ${1:.2f} -- ${2:.2f} -- ${3:.2f} -- ${4:.2f} -- from BrickLink'.format(
				price_data.get('item_id'),
				float(price_data.get( 'new_median_sale_price'))/100.,
				float(price_data.get('used_median_sale_price'))/100.,
				float(price_data.get( 'new_median_list_price'))/100.,
				float(price_data.get('used_median_list_price'))/100.,
			))
		self.bricklink_price_cache[item_id] = price_data
		self.price_count += 1
		if self.price_count % 10 == 0:
			self.save_cache(single_cache_name='bricklink_price_cache')
		return price_data

	#============================
	#============================
	def getSetPriceDetails(self, legoID, guide_type='sold', new_or_used='U',
			country_code='US', currency_code='USD', verbose=True):
		""" get price details from BrickLink using an integer legoID """
		#https://www.bricklink.com/v3/api.page?page=get-price-guide
		self._check_lego_ID(legoID)
		###################
		url = 'items/set/{0}-1/price?guide_type={1}&new_or_used={2}&country_code={3}&currency_code={4}'.format(
			legoID, guide_type, new_or_used, country_code, currency_code)
		price_details = self._bricklink_get(url)
		qty = price_details['total_quantity']
		###################
		if verbose is True and qty > 1:
			avg_price = float(price_details['avg_price'])
			print('SET {0} -- ${1:.2f} average price for {2} sales -- from BrickLink website'.format(
				legoID, avg_price, qty))
		return price_details

	#============================
	#============================
	def getSetPriceData(self, legoID, verbose=False):
		""" compile price data from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		###################
		price_data = self._lookUpPriceDataCache(legoID, verbose)
		if price_data is not None:
			return price_data
		###################
		used_price_sale_details = self.getSetPriceDetails(legoID, guide_type='sold', new_or_used='U', verbose=verbose)
		new_price_sale_details 	= self.getSetPriceDetails(legoID, guide_type='sold', new_or_used='N', verbose=verbose)
		used_price_list_details = self.getSetPriceDetails(legoID, guide_type='stock', new_or_used='U', verbose=verbose)
		new_price_list_details 	= self.getSetPriceDetails(legoID, guide_type='stock', new_or_used='N', verbose=verbose)
		price_data = self._compilePriceData(legoID,
			new_price_sale_details, used_price_sale_details,
			new_price_list_details, used_price_list_details)
		return price_data

	#============================
	#============================
	def getMinifigPriceDetails(self, minifigID, guide_type='sold', new_or_used='U',
			country_code='US', currency_code='USD', verbose=True):
		""" get price details from BrickLink using an string minifigID """
		###################
		url = 'items/minifig/{0}/price?guide_type={1}&new_or_used={2}&country_code={3}&currency_code={4}'.format(
			minifigID, guide_type, new_or_used, country_code, currency_code)
		price_details = self._bricklink_get(url)
		###################
		avg_price = float(price_details['avg_price'])
		qty = price_details['total_quantity']
		if verbose is True and qty > 1:
			print('MINIFIG {0} -- ${1:.2f} average price for {2} sales -- from BrickLink website'.format(
				minifigID, avg_price, qty))
		return price_details

	#============================
	#============================
	def getMinifigsPriceData(self, minifigID, verbose=False):
		""" compile price data from BrickLink using an string minifigID """
		price_data = self._lookUpPriceDataCache(minifigID, verbose)
		if price_data is not None:
			return price_data
		used_price_sale_details = self.getMinifigPriceDetails(minifigID, guide_type='sold', new_or_used='U', verbose=verbose)
		new_price_sale_details 	= self.getMinifigPriceDetails(minifigID, guide_type='sold', new_or_used='N', verbose=verbose)
		used_price_list_details = self.getMinifigPriceDetails(minifigID, guide_type='stock', new_or_used='U', verbose=verbose)
		new_price_list_details 	= self.getMinifigPriceDetails(minifigID, guide_type='stock', new_or_used='N', verbose=verbose)
		price_data = self._compilePriceData(minifigID,
			new_price_sale_details, used_price_sale_details,
			new_price_list_details, used_price_list_details)
		return price_data

	#============================
	#============================
	def getSetIDsFromSet(self, legoID, verbose=True):
		""" get list of set data dicts from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		###################
		set_id_tree = self.bricklink_subset_cache.get(legoID)
		if set_id_tree is not None and isinstance(set_id_tree, list):
			if verbose is True:
				print('SET {0} -- {1} sub-sets -- from cache'.format(legoID, len(set_id_tree)))
			return set_id_tree
		###################
		subsets_tree = self.getPartsFromSet(legoID, verbose=False)
		set_id_tree = []
		for part in subsets_tree:
			for entry in part['entries']:
				item = entry['item']
				if item['type'] != 'SET':
					continue
				setID = item['no']
				#qty = entry.get('quantity', 1)
				qty = entry['quantity']
				for qi in range(qty):
					set_id_tree.append(setID)
		set_id_tree.sort()
		if verbose is True:
			print('SET {0} -- {1} sub-sets -- from BrickLink website'.format(legoID, len(set_id_tree)))
		self.bricklink_subset_cache[legoID] = set_id_tree
		return set_id_tree

	#============================
	#============================
	def getMinifigIDsFromSet(self, legoID, verbose=True):
		""" get list of minifig data dicts from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		###################
		minifig_id_tree = self.bricklink_minifig_set_cache.get(legoID)
		if minifig_id_tree is not None and isinstance(minifig_id_tree, list):
			if verbose is True:
				print('SET {0} -- {1} minifigs -- from cache'.format(legoID, len(minifig_id_tree)))
			return minifig_id_tree
		###################
		subsets_tree = self.getPartsFromSet(legoID, verbose=False)
		minifig_id_tree = []
		for part in subsets_tree:
			for entry in part['entries']:
				item = entry['item']
				if item['type'] != 'MINIFIG':
					continue
				minifigID = item['no']
				#qty = entry.get('quantity', 1)
				qty = entry['quantity']
				for qi in range(qty):
					minifig_id_tree.append(minifigID)
		minifig_id_tree.sort()
		if verbose is True:
			print('SET {0} -- {1} minifigs -- from BrickLink website'.format(legoID, len(minifig_id_tree)))
		self.bricklink_minifig_set_cache[legoID] = minifig_id_tree
		return minifig_id_tree

	#============================
	#============================
	def getMinifigData(self, minifigID, verbose=True):
		""" get individual minifig data from BrickLink using an string minifigID """

		###################
		minifig_data = self.bricklink_minifig_cache.get(minifigID)
		if self._check_if_data_valid(minifig_data) is True:
			if verbose is True:
				print('MINIFIG {0} -- {1} ({2}) -- from cache'.format(
					minifig_data.get('no'), minifig_data.get('name'), minifig_data.get('year_released'),))
			return minifig_data
		###################
		minifig_data = self._bricklink_get('items/minifig/{0}'.format(minifigID))
		###################
		#print(minifig_data)
		if verbose is True:
			print('MINIFIG {0} -- {1} ({2}) -- from BrickLink website'.format(
				minifigID, minifig_data.get('name')[:60], minifig_data.get('year_released'),))
		self.bricklink_minifig_cache[minifigID] = minifig_data
		return minifig_data

	#============================
	#============================
	def getPartData(self, partID, verbose=True):
		""" get individual part data from BrickLink using an string minifigID """
		###################
		part_data = self.bricklink_part_cache.get(partID)
		if self._check_if_data_valid(part_data) is True:
			if verbose is True:
				print('PART {0} -- {1} ({2}) -- from cache'.format(
					part_data.get('no'), part_data.get('name'), part_data.get('year_released'),))
			return part_data
		###################
		part_data = self._bricklink_get('items/part/{0}'.format(partID))
		###################
		#print(part_data)
		if verbose is True:
			print('PART {0} -- {1} ({2}) -- from BrickLink website'.format(
				partID, part_data.get('name'),part_data.get('year_released'),))
		self.bricklink_part_cache[partID] = part_data
		return part_data


if __name__ == "__main__":
	BL = BrickLink()
	price_data = BL.getSetPriceData(75151)
	import pprint
	pprint.pprint(price_data)
	BL.close()
