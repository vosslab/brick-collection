import libbrick.image_cache
import super_make_set_labels

#============================
#============================
def test_make_label_includes_msrp(monkeypatch):
	"""
	Adds MSRP line when cache has a value.
	"""
	monkeypatch.setattr(
		libbrick.image_cache,
		"get_cached_image",
		lambda *args, **kwargs: "images/processed/set_123-1.png",
	)
	set_dict = {
		'set_id': '123-1',
		'name': 'Test Set',
		'category_name': 'Theme',
		'year_released': 2020,
		'num_parts': 123,
		'theme_name': 'Theme',
		'year': 2020,
		'set_img_url': 'https://example.com/x.jpg',
	}
	msrp_cache = {'123-1': 4999}
	result = super_make_set_labels.makeLabel(set_dict, msrp_cache)
	assert r"MSRP: \$49.99" in result

#============================

def test_make_label_without_msrp(monkeypatch):
	"""
	Skips MSRP line when cache is missing.
	"""
	monkeypatch.setattr(
		libbrick.image_cache,
		"get_cached_image",
		lambda *args, **kwargs: "images/processed/set_123-1.png",
	)
	set_dict = {
		'set_id': '123-1',
		'name': 'Test Set',
		'category_name': 'Theme',
		'year_released': 2020,
		'num_parts': 123,
		'theme_name': 'Theme',
		'year': 2020,
		'set_img_url': 'https://example.com/x.jpg',
	}
	msrp_cache = {}
	result = super_make_set_labels.makeLabel(set_dict, msrp_cache)
	assert 'MSRP' not in result
