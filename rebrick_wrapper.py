
import sys
import time
import yaml
import random
import rebrick
import wrapper_base

class ReBrick(wrapper_base.BaseWrapperClass):
	#============================
	#============================
	def __init__(self):
		self.debug = True
		self.api_data = yaml.safe_load(open('rebrick_api_private.yml', 'r'))
		self.rebrick_api = rebrick.api.rebrickAPI(
		  self.api_data['consumer_key'], self.api_data['consumer_secret'],
		  self.api_data['token_value'], self.api_data['token_secret'])

		self.data_caches = {
			'rebrick_theme_cache': 	'yaml',
			'rebrick_set_cache':	'json',
		}
		self.start()

	#============================
	#============================
	def _rebrick_get(self, url):
		""" common function for all API calls """
		#random sleep of 0-1 seconds to help server load
		time.sleep(random.random())
		sys.exit(1)
		#return data_dict
