
import os
import sys
import time
import yaml
import random
import statistics
import bricklink.api

class BrickLink(object):
	#============================
	#============================
	def __init__(self):
		self.load_cache()
		self.expire_time = 1000
		self.data_refresh_cutoff = 0.1

	#============================
	#============================
	def close(self):
		self.save_cache()

	#============================
	#============================
	def load_cache(self):
		print('==== LOAD CACHE ====')
		self.debug = True
		self.api_data = yaml.safe_load(open('bricklink_api_private.yml', 'r'))
		self.bricklink_api = bricklink.api.BrickLinkAPI(
		  self.api_data['consumer_key'], self.api_data['consumer_secret'],
		  self.api_data['token_value'], self.api_data['token_secret'])

		self.data_caches = [
			'bricklink_category_cache',
			'bricklink_minifig_cache',
			'bricklink_minifig_set_cache',
			'bricklink_part_cache',
			'bricklink_price_cache',
			'bricklink_set_brick_weight_cache',
			'bricklink_set_cache',
			'bricklink_subsets_cache',
		]

		for cache_name in self.data_caches:
			file_name = 'CACHE/'+cache_name+'.yml'
			if os.path.isfile(file_name):
				try:
					cache_data =  yaml.safe_load( open(file_name, 'r') )
					print('.. loaded {0} entires from {1}'.format(len(cache_data), file_name))
				except IOError:
					cache_data = {}
			else:
				cache_data = {}
			setattr(self, cache_name, cache_data)
		#print(getattr(self, 'bricklink_set_cache').keys())
		print('==== END CACHE ====')

	#============================
	#============================
	def save_cache(self):
		print('==== SAVE CACHE ====')
		if not os.path.isdir('CACHE'):
			os.mkdir('CACHE')
		for cache_name in self.data_caches:
			file_name = 'CACHE/'+cache_name+'.yml'
			cache_data = getattr(self, cache_name)
			if len(cache_data) > 0:
				yaml.dump( cache_data, open( file_name, 'w') )
				print('.. wrote {0} entires to {1}'.format(len(cache_data), file_name))
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
	def _bricklink_get(self, url):
		""" common function for all API calls """
		#random sleep of 0-1 seconds to help server load
		time.sleep(random.random())
		status, headers, response = self.bricklink_api.get(url)
		error_msg = False
		if ( response.get('data') is None
			 or len(response.get('data')) == 0):
			error_msg = True
		if error_msg is True:
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
				print('PRICE {0} -- ${1:.2f} -- ${2:.2f} -- from cache'.format(
					price_data.get('item_id'), float(price_data.get('new_median_price'))/100.,
					float(price_data.get('used_median_price'))/100.,))
			return price_data
		###################
		return None

	#============================
	#============================
	def _compilePriceData(self, item_id, new_price_data, used_price_data, verbose=True):
		###################
		used_avg_price 	= int(float(used_price_data['avg_price'])*100)
		used_qty 		= int(used_price_data['total_quantity'])
		new_avg_price 	= int(float(new_price_data['avg_price'])*100)
		new_qty 		= int(new_price_data['total_quantity'])
		###################
		# New Sales
		new_prices = []
		for item in new_price_data['price_detail']:
			new_prices.append(int(float(item['unit_price'])*100))
		#print(new_prices)
		if new_qty >= 1:
			new_median_price = int(statistics.median(new_prices))
		else:
			new_median_price = -1
		#print(new_median_price)
		###################
		# Used Sales
		used_prices = []
		for item in used_price_data['price_detail']:
			used_prices.append(int(float(item['unit_price'])*100))
		#print(used_prices)
		if used_qty >= 1:
			used_median_price = int(statistics.median(used_prices))
		else:
			used_median_price = -1
		#print(used_median_price)
		###################
		price_data = {
			'item_id':				item_id,
			'new_avg_price': 		new_avg_price,
			'new_median_price': 	new_median_price,
			'new_qty': 				new_qty,
			'used_avg_price': 		used_avg_price,
			'used_median_price': 	used_median_price,
			'used_qty': 			used_qty,
			'time':					int(time.time()),
		}
		if verbose is True:
			print('PRICE {0} -- ${1:.2f} -- ${2:.2f} -- from BrickLink'.format(
				price_data.get('item_id'), float(price_data.get('new_median_price'))/100.,
				float(price_data.get('used_median_price'))/100.,))
		self.bricklink_price_cache[item_id] = price_data
		return price_data

	#============================
	#============================
	def getSetPriceDetails(self, legoID, new_or_used='U', country_code='US', currency_code='USD', verbose=True):
		""" get price details from BrickLink using an integer legoID """
		self._check_lego_ID(legoID)
		###################
		url = 'items/set/{0}-1/price?guide_type=sold&new_or_used={1}&country_code={2}&currency_code={3}'.format(
			legoID, new_or_used, country_code, currency_code)
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
		used_price_details = self.getSetPriceDetails(legoID, new_or_used='U', verbose=verbose)
		new_price_details 	= self.getSetPriceDetails(legoID, new_or_used='N', verbose=verbose)
		price_data = self._compilePriceData(legoID, new_price_details, used_price_details)
		return price_data

	#============================
	#============================
	def getMinifigPriceDetails(self, minifigID, new_or_used='U', country_code='US', currency_code='USD', verbose=True):
		""" get price details from BrickLink using an string minifigID """
		###################
		url = 'items/minifig/{0}/price?guide_type=sold&new_or_used={1}&country_code={2}&currency_code={3}'.format(
			minifigID, new_or_used, country_code, currency_code)
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
		used_price_details = self.getMinifigPriceDetails(minifigID, new_or_used='U', verbose=verbose)
		new_price_details 	= self.getMinifigPriceDetails(minifigID, new_or_used='N', verbose=verbose)
		price_data = self._compilePriceData(minifigID, new_price_details, used_price_details)
		return price_data

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
		set_data = self.getSetData(legoID, verbose=False)
		subsets_tree = self.getPartsFromSet(legoID, verbose=False)
		minifig_id_tree = []
		key_list = ['name', 'no', 'image_url', 'year_released', 'weight']
		for part in subsets_tree:
			for entry in part['entries']:
				item = entry['item']
				if item['type'] != 'MINIFIG':
					continue
				minifigID = item['no']
				minifig_id_tree.append(minifigID)
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
