
import os
import sys
import time
import yaml
import json

class BaseWrapperClass(object):
	#============================
	#============================
	def __init__(self):
		self.api_key = None
		self.data_caches = {
			'wrapper_test_json_cache': 'json',
			'wrapper_test_yaml_cache': 'yaml',
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
			file_name = 'CACHE/'+cache_name+'.'+cache_format
			if os.path.isfile(file_name):
				try:
					t0 = time.time()
					if cache_format == 'json':
						cache_data = json.load( open(file_name, 'r') )
					elif cache_format == 'yml':
						cache_data =  yaml.safe_load( open(file_name, 'r') )
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
	def save_cache(self):
		print('==== SAVE CACHE ====')
		if not os.path.isdir('CACHE'):
			os.mkdir('CACHE')
		for cache_name,cache_format in self.data_caches.items():
			t0 = time.time()
			file_name = 'CACHE/'+cache_name+'.'+self.cache_format
			cache_data = getattr(self, cache_name)
			if len(cache_data) > 0:
				if cache_format == 'json':
					json.dump( cache_data, open( file_name, 'w') )
				elif cache_format == 'yml':
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
