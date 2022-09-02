
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
				cache_data =  yaml.safe_load( open(file_name, 'r') )
				print('.. loaded {0} entires from {1}'.format(len(cache_data), file_name))
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
			file_name = 'CACHE/'+cache_name+'.yml'
			cache_data = getattr(self, cache_name)
			if len(cache_data) > 0:
				yaml.dump( cache_data, open( file_name, 'w') )
				print('.. wrote {0} entires to {1}'.format(len(cache_data), file_name))
		print('==== END CACHE ====')

	#============================
	#============================
	def _check_lego_ID(self, legoID):
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
	def bricklink_get(self, url):
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
		return response['data']

	#============================
	#============================
	def getCategoryName(self, categoryID):
		category_name = self.bricklink_category_cache.get(categoryID)
		if category_name is not None:
			return category_name
		###################
		category_data = self.bricklink_get('categories/{0}'.format(categoryID))
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
		self._check_lego_ID(legoID)
		set_data = self.bricklink_set_cache.get(legoID)
		if set_data is not None:
			if verbose is True:
				print('SET {0} -- {1} ({2}) -- from cache'.format(
					set_data.get('no'), set_data.get('name'), set_data.get('year_released'),))
			set_data['category_name'] = self.getCategoryName(set_data['category_id'])
			set_data['set_num'] = legoID
			self.bricklink_set_cache[legoID] = set_data
			return set_data
		###################
		set_data = self.bricklink_get('items/set/{0}-1'.format(legoID))
		###################
		set_data['category_name'] = self.getCategoryName(set_data['category_id'])
		if verbose is True:
			print('SET {0} -- {1} ({2}) -- from BrickLink website'.format(
				set_data.get('no'), set_data.get('name'), set_data.get('year_released'),))
		set_data['time'] = int(time.time())
		set_data['set_num'] = legoID
		self.bricklink_set_cache[legoID] = set_data
		return set_data

	#============================
	#============================
	def getSetDataDirect(self, setID, verbose=True):
		set_data = self.bricklink_set_cache.get(setID)
		if set_data is not None:
			if verbose is True:
				print('SET {0} -- {1} ({2}) -- from cache'.format(
					set_data.get('no'), set_data.get('name'), set_data.get('year_released'),))
			set_data['category_name'] = self.getCategoryName(set_data['category_id'])
			self.bricklink_set_cache[legoID] = set_data
			return set_data
		###################
		set_data = self.bricklink_get('items/set/{0}'.format(setID))
		###################
		set_data['category_name'] = self.getCategoryName(set_data['category_id'])
		if verbose is True:
			print('SET {0} -- {1} ({2}) -- from BrickLink website'.format(
				set_data.get('no'), set_data.get('name'), set_data.get('year_released'),))

		set_data['time'] = int(time.time())
		self.bricklink_set_cache[legoID] = set_data
		return set_data

	#============================
	#============================
	def getPartsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		if self.debug is True:
			## this is TOO BIG, cache just not worth it
			subsets_tree = self.bricklink_subsets_cache.get(legoID)
			if subsets_tree is not None and verbose is True:
				print('SET {0} -- {1} parts -- from cache'.format(legoID, len(subsets_tree)))
				return subsets_tree
		###################
		subsets_tree = self.bricklink_get('items/set/{0}-1/subsets'.format(legoID))
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
		self._check_lego_ID(legoID)
		set_data = self.getSetData(legoID, verbose=False)
		string_weight = self.bricklink_set_brick_weight_cache.get(legoID)
		if string_weight is not None:
			if verbose is True:
				print('SET {0} -- {1} grams -- from set data'.format(legoID, set_data['weight']))
				print('SET {0} -- {1} grams -- from cache'.format(legoID, string_weight))
			return string_weight
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
	def getSetPriceDetails(self, legoID, new_or_used='U', country_code='US', currency_code='USD', verbose=True):
		self._check_lego_ID(legoID)
		###################
		url = 'items/set/{0}-1/price?guide_type=sold&new_or_used={1}&country_code={2}&currency_code={3}'.format(
			legoID, new_or_used, country_code, currency_code)
		price_data = self.bricklink_get(url)
		###################
		avg_price = float(price_data['avg_price'])
		qty = price_data['total_quantity']
		if verbose is True and qty > 1:
			print('SET {0} -- ${1:.2f} average price for {2} sales -- from BrickLink website'.format(
				legoID, avg_price, qty))
		return price_data

	#============================
	#============================
	def getSetPriceData(self, legoID, verbose=False):
		self._check_lego_ID(legoID)
		price_data = self.lookUpPriceDataCache(legoID, verbose)
		if price_data is not None:
			return price_data
		used_price_data = self.getSetPriceDetails(legoID, new_or_used='U', verbose=verbose)
		new_price_data 	= self.getSetPriceDetails(legoID, new_or_used='N', verbose=verbose)
		price_data = self.compilePriceData(legoID, new_price_data, used_price_data)
		return price_data

	#============================
	#============================
	def lookUpPriceDataCache(self, item_id, verbose=True):
		price_data = self.bricklink_price_cache.get(item_id)
		if random.random() > 0.1 and price_data is not None:
			if verbose is True:
				print('PRICE {0} -- ${1:.2f} -- ${2:.2f} -- from cache'.format(
					price_data.get('item_id'), float(price_data.get('new_median_price'))/100.,
					float(price_data.get('used_median_price'))/100.,))
			if time.time() - price_data['time'] < 10000:
				return price_data
		return None

	#============================
	#============================
	def compilePriceData(self, item_id, new_price_data, used_price_data, verbose=True):
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
		new_median_price = int(statistics.median(new_prices))
		#print(new_median_price)
		###################
		# Used Sales
		used_prices = []
		for item in used_price_data['price_detail']:
			used_prices.append(int(float(item['unit_price'])*100))
		#print(used_prices)
		used_median_price = int(statistics.median(used_prices))
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
	def getMinifigPriceDetails(self, minifigID, new_or_used='U', country_code='US', currency_code='USD', verbose=True):
		###################
		url = 'items/minifig/{0}/price?guide_type=sold&new_or_used={1}&country_code={2}&currency_code={3}'.format(
			minifigID, new_or_used, country_code, currency_code)
		price_data = self.bricklink_get(url)
		###################
		avg_price = float(price_data['avg_price'])
		qty = price_data['total_quantity']
		if verbose is True and qty > 1:
			print('MINIFIG {0} -- ${1:.2f} average price for {2} sales -- from BrickLink website'.format(
				minifigID, avg_price, qty))
		return price_data

	#============================
	#============================
	def getMinifigsPriceData(self, minifigID, verbose=False):
		price_data = self.lookUpPriceDataCache(minifigID, verbose)
		if price_data is not None:
			return price_data
		used_price_data = self.getMinifigPriceDetails(minifigID, new_or_used='U', verbose=verbose)
		new_price_data 	= self.getMinifigPriceDetails(minifigID, new_or_used='N', verbose=verbose)
		price_data = self.compilePriceData(minifigID, new_price_data, used_price_data)
		return price_data

	#============================
	#============================
	def getMinifigsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		minifig_set_tree = self.bricklink_minifig_set_cache.get(legoID)
		if minifig_set_tree is not None:
			if verbose is True:
				print('SET {0} -- {1} minifigs -- from cache'.format(legoID, len(minifig_set_tree)))
			return minifig_set_tree
		set_data = self.getSetData(legoID, verbose=False)
		subsets_tree = self.getPartsFromSet(legoID, verbose=False)
		minifig_set_tree = []
		key_list = ['name', 'no', 'image_url', 'year_released', 'weight']
		for part in subsets_tree:
			for entry in part['entries']:
				item = entry['item']
				if item['type'] != 'MINIFIG':
					continue
				minifigID = item['no']
				#item_plus = self.getSetDataDirect(item['no'])
				minifig_data = self.getMinifigData(minifigID)
				minifig_dict = {}
				for key in key_list:
					minifig_dict[key] = minifig_data.get(key)
				minifig_dict['set_num'] = legoID
				minifig_dict['minifig_id'] = minifigID
				minifig_dict['set_image_url'] = set_data['image_url']

				for i in range(int(entry['quantity'])):
					minifig_set_tree.append(minifig_dict)
		if verbose is True:
			print('SET {0} -- {1} minifigs -- from BrickLink website'.format(legoID, len(minifig_set_tree)))
		self.bricklink_minifig_set_cache[legoID] = minifig_set_tree
		return minifig_set_tree

	#============================
	#============================
	def getMinifigData(self, minifigID, verbose=True):
		minifig_data = self.bricklink_minifig_cache.get(minifigID)
		if random.random() > 0.1 and minifig_data is not None:
			if verbose is True:
				print('MINIFIG {0} -- {1} ({2}) -- from cache'.format(
					minifig_data.get('no'), minifig_data.get('name'), minifig_data.get('year_released'),))
			return minifig_data
		###################
		minifig_data = self.bricklink_get('items/minifig/{0}'.format(minifigID))
		###################
		#print(minifig_data)
		if verbose is True:
			print('MINIFIG {0} -- {1} ({2}) -- from BrickLink website'.format(
				minifigID, minifig_data.get('name')[:60], minifig_data.get('year_released'),))

		minifig_data['time'] = int(time.time())
		self.bricklink_minifig_cache[minifigID] = minifig_data
		return minifig_data

	#============================
	#============================
	def getPartData(self, partID, verbose=True):
		part_data = self.bricklink_part_cache.get(partID)
		if part_data is not None:
			if verbose is True:
				print('PART {0} -- {1} ({2}) -- from cache'.format(
					part_data.get('no'), part_data.get('name'), part_data.get('year_released'),))
			return part_data
		###################
		part_data = self.bricklink_get('items/part/{0}'.format(partID))
		###################
		#print(part_data)
		if verbose is True:
			print('PART {0} -- {1} ({2}) -- from BrickLink website'.format(
				partID, part_data.get('name'),part_data.get('year_released'),))

		part_data['time'] = int(time.time())
		self.bricklink_part_cache[partID] = part_data
		return part_data
