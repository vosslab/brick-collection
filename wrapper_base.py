
import os
import sys
import json
import time
import yaml
import random

class BaseWrapperClass(object):
	#============================
	#============================
	def __init__(self):
		self.api_key = None

		# YAML is more readable than JSON
		# YAML like PYHTON uses indentation to indicate levels
		# YAML has a ton of features, including comments and relational anchors
		# YAML can sometimes allow an attacker to execute arbitrary code

		# JSON is much faster because of significantly less features
		# JSON is a subset of JavaScript with bracketed syntax
		# JSON uses less characters because it doesn't use whitespace to represent hierarchy
		# JSON allows duplicate keys, which is invalid PYTHON and YAML
		# JSON is prferred by web developers for APIs, many web programmers are not aware YAML exists

		# When the CACHE file is BIG and contains lots of details... use JSON
		# When the CACHE file is SIMPLE and might require EDITING... use YAML/YML

		self.data_caches = {
			'wrapper_test_json_cache': 'json',
			'wrapper_test_yaml_cache': 'yml',
		}
		self.start()

	#============================
	#============================
	def start(self):
		self.expire_time = 14 * 24 * 3600 # 14 days, in seconds
		self.data_refresh_cutoff = 0.01 # 1% of the data is refreshed
		self.api_calls = 0
		self.api_log = []
		self.load_cache()

	#============================
	#============================
	def load_cache(self):
		print('==== LOAD CACHE ====')
		for cache_name,cache_format in self.data_caches.items():
			if cache_format == 'yaml':
				cache_format = 'yml'
			file_name = 'CACHE/'+cache_name+'.'+cache_format
			if os.path.isfile(file_name):
				try:
					t0 = time.time()
					if cache_format == 'json':
						cache_data = json.load( open(file_name, 'r') )
					elif cache_format == 'yml':
						cache_data =  yaml.safe_load( open(file_name, 'r') )
					else:
						print("UNKNOWN CACHE FORMAT: ", cache_data)
						sys.exit(1)
					print('.. loaded {0} entires from {1} in {2:d} usec'.format(
						len(cache_data), file_name, int((time.time()-t0)*1e6)))
				except IOError:
					cache_data = {}
			else:
				cache_data = {}
			setattr(self, cache_name, cache_data)
		print('==== END CACHE ====')

	#============================
	#============================
	def close(self):
		self.save_cache()
		#self.api_log.sort()
		#print(self.api_log)
		print("{0} api calls were made".format(self.api_calls))

	#============================
	#============================
	def save_cache(self, single_cache_name=None):
		print('==== SAVE CACHE ====')
		if not os.path.isdir('CACHE'):
			os.mkdir('CACHE')
		for cache_name, cache_format in self.data_caches.items():
			if single_cache_name is not None and single_cache_name != cache_name:
				#print('.. skipping cache: ', cache_name)
				continue
			if cache_format == 'yaml':
				cache_format = 'yml'
			t0 = time.time()
			file_name = 'CACHE/'+cache_name+'.'+cache_format
			cache_data = getattr(self, cache_name)
			if len(cache_data) > 0:
				if cache_format == 'json':
					json.dump( cache_data, open( file_name, 'w') )
				elif cache_format == 'yml':
					yaml.dump( cache_data, open( file_name, 'w') )
				else:
					print("UNKNOWN CACHE FORMAT: ", cache_data)
					sys.exit(1)
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
			print('... no time in cache')
			return False
		###################
		if time.time() - int(cache_data_dict.get('time')) > self.expire_time:
			print('... cache expired')
			return False
		###################
		if random.random() < self.data_refresh_cutoff:
			print('... random data refresh')
			# reset data to None, 10% of the time
			# keeps the data fresh
			return False
		###################
		return True

#============================
#============================
