
import os
import sys
import time
import yaml
import random
import rebrick
import statistics

class ReBrick(object):
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
		self.api_data = yaml.safe_load(open('rebrick_api_private.yml', 'r'))
		self.rebrick_api = rebrick.api.rebrickAPI(
		  self.api_data['consumer_key'], self.api_data['consumer_secret'],
		  self.api_data['token_value'], self.api_data['token_secret'])

		self.data_caches = [
			'rebrick_theme_cache',
			'rebrick_set_cache',
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
		#print(getattr(self, 'rebrick_set_cache').keys())
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
	def _rebrick_get(self, url):
		""" common function for all API calls """
		#random sleep of 0-1 seconds to help server load
		time.sleep(random.random())
		sys.exit(1)
		return data_dict

	#============================
	#============================
	def _check_if_data_valid(self, cache_data_dict):
		""" common function of data expiration """
		if cache_data_dict is None:
			return False
		###################
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
