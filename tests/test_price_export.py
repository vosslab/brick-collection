"""
Tests for libbrick.price_export module.
"""

import libbrick.price_export


#============================================
def test_format_number_human_zero():
	"""format_number_human(0) should return '0'."""
	result = libbrick.price_export.format_number_human(0)
	assert result == '0'
	assert 'e' not in result.lower()


#============================================
def test_format_number_human_small_decimal():
	"""format_number_human(0.3) avoids scientific notation."""
	result = libbrick.price_export.format_number_human(0.3)
	assert 'e' not in result.lower()
	# Should be something like '0.3'
	assert float(result) == 0.3


#============================================
def test_format_number_human_very_small():
	"""format_number_human(1.234e-10) avoids scientific notation."""
	result = libbrick.price_export.format_number_human(1.234e-10)
	assert 'e' not in result.lower()


#============================================
def test_format_number_human_very_large():
	"""format_number_human(1.234e9) avoids scientific notation."""
	result = libbrick.price_export.format_number_human(1.234e9)
	assert 'e' not in result.lower()
	# Result should be a plain number
	assert float(result) > 1e9


#============================================
def test_format_number_human_large_int():
	"""format_number_human(1234567) avoids scientific notation."""
	result = libbrick.price_export.format_number_human(1234567)
	assert 'e' not in result.lower()
	assert 'E' not in result
	assert result == '1234567'


#============================================
def test_process_value_long_url_not_truncated():
	"""process_value does not truncate URLs."""
	long_suffix = 'a' * 200
	url = 'http://x/y' + long_suffix
	result = libbrick.price_export.process_value(url)
	assert result.startswith('http://')
	assert len(result) > 70
	assert result == url


#============================================
def test_process_value_long_string_truncated():
	"""process_value truncates non-URL strings to exactly 70 chars."""
	long_string = 'a' * 200
	result = libbrick.price_export.process_value(long_string)
	assert len(result) == 70
	assert result == 'a' * 70


#============================================
def test_build_image_urls_part_type():
	"""build_image_urls for PART type returns correct URL templates."""
	urls = libbrick.price_export.build_image_urls(
		element_id=6314891,
		part_id='3021',
		color_id=103,
		item_type='PART',
		item_id=None,
	)
	assert urls['lego_image_url'] == (
		'https://www.lego.com/cdn/product-assets/element.img.lod5photo.192x192/6314891.jpg'
	)
	assert urls['rebrickable_image_url'] == (
		'https://cdn.rebrickable.com/media/thumbs/parts/elements/6314891.jpg/250x250p.jpg'
	)
	assert urls['bricklink_image_url'] == (
		'https://img.bricklink.com/ItemImage/PN/103/3021.png'
	)


#============================================
def test_build_image_urls_minifig_type():
	"""build_image_urls for MINIFIG type returns correct bricklink URL."""
	urls = libbrick.price_export.build_image_urls(
		element_id=None,
		part_id=None,
		color_id=None,
		item_type='MINIFIG',
		item_id='sc118',
	)
	assert urls['bricklink_image_url'] == (
		'https://img.bricklink.com/ItemImage/MN/0/sc118.original.png'
	)
	assert urls['lego_image_url'] == ''
	assert urls['rebrickable_image_url'] == ''


#============================================
class FakeImageChecker:
	"""Stub for testing pick_valid_image_url."""

	def __init__(self, existing):
		"""
		Initialize with dict mapping URL to True/False.

		Args:
			existing: dict with URL keys and boolean values.
		"""
		self.existing = existing

	def image_exists(self, url):
		"""Return whether image exists in our stub data."""
		return self.existing.get(url, False)


#============================================
def test_pick_valid_image_url_returns_first_match():
	"""pick_valid_image_url returns first valid URL in priority order."""
	checker = FakeImageChecker({
		'https://url1.jpg': False,
		'https://url2.jpg': True,
		'https://url3.jpg': True,
	})
	urls = ['https://url1.jpg', 'https://url2.jpg', 'https://url3.jpg']
	result = libbrick.price_export.pick_valid_image_url(checker, urls)
	assert result == 'https://url2.jpg'


#============================================
def test_pick_valid_image_url_returns_empty_when_none_match():
	"""pick_valid_image_url returns '' when no URLs are valid."""
	checker = FakeImageChecker({
		'https://url1.jpg': False,
		'https://url2.jpg': False,
	})
	urls = ['https://url1.jpg', 'https://url2.jpg']
	result = libbrick.price_export.pick_valid_image_url(checker, urls)
	assert result == ''


#============================================
def test_pick_valid_image_url_skips_empty_strings():
	"""pick_valid_image_url skips empty/falsy URLs."""
	checker = FakeImageChecker({
		'https://url1.jpg': True,
	})
	urls = ['', None, 'https://url1.jpg']
	result = libbrick.price_export.pick_valid_image_url(checker, urls)
	assert result == 'https://url1.jpg'
