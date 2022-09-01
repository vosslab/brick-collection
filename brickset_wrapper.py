
import os
import sys
import time
import yaml
import random
import brickfront

class BrickSet(object):
	#============================
	#============================
	def __init__(self):
		print('==== LOAD CACHE ====')
		self.debug = True
		self.api_data = yaml.safe_load(open('brickset_api_private.yml', 'r'))
		self.brickset_client = brickfront.Client(self.api_data['api_key'])

		self.data_caches = [
			'brickset_category_cache',
			'brickset_set_cache',
			'brickset_part_cache',
			'brickset_subsets_cache',
			'brickset_minifig_cache',
			'brickset_minifig_set_cache',
			'brickset_set_brick_weight_cache',
		]

		for cache_name in self.data_caches:
			file_name = 'CACHE/'+cache_name+'.yml'
			if os.path.isfile(file_name):
				cache_data =  yaml.safe_load( open(file_name, 'r') )
				print('.. loaded {0} entires from {1}'.format(len(cache_data), file_name))
			else:
				cache_data = {}
			setattr(self, cache_name, cache_data)
		#print(getattr(self, 'brickset_set_cache').keys())
		print('==== END CACHE ====')


	#============================
	#============================
	def close(self):
		self.save_cache()

	#============================
	#============================
	def save_cache(self):
		print('==== SAVE CACHE ====')
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
	def brickset_get(self, url):
		time.sleep(random.random())
		status, headers, response = self.brickset_api.get(url)
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
		pass
		return category_name

	#============================
	#============================
	def getSetData(self, legoID, verbose=True):
		pass
		return set_data

	#============================
	#============================
	def getSetDataDirect(self, setID, verbose=True):
		pass
		return set_data

	#============================
	#============================
	def getPartsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		pass
		return subsets_tree

	#============================
	#============================
	def getSetBrickWeight(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		pass
		return string_weight

	#============================
	#============================
	def getSetPriceDetails(self, legoID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		self._check_lego_ID(legoID)
		pass
		return price_data

	#============================
	#============================
	def getMinifigPriceDetails(self, minifigID, new_or_used='U', country_code='US',
			currency_code='USD', verbose=True):
		pass
		return price_data

	#============================
	#============================
	def getMinifigsPrice(self, minifigID):
		pass
		return avg_price, sales

	#============================
	#============================
	def getMinifigsFromSet(self, legoID, verbose=True):
		self._check_lego_ID(legoID)
		pass
		return minifig_set_tree

	#============================
	#============================
	def getMinifigData(self, minifigID, verbose=True):
		pass
		return minifig_data

	#============================
	#============================
	def getPartData(self, partID, verbose=True):
		pass
		return part_data
