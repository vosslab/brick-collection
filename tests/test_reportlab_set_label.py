import reportlab_make_set_labels


#============================================
def test_make_set_label_data_includes_msrp() -> None:
	"""
	MSRP text appears when cache has a valid value.
	"""
	set_dict = {
		"set_id": "123-1",
		"name": "Test Set",
		"category_name": "Theme",
		"year_released": 2020,
		"num_parts": 123,
		"theme_name": "Theme",
		"year": 2020,
		"set_img_url": "https://example.com/x.jpg",
	}
	data = reportlab_make_set_labels.make_set_label_data(set_dict, {"123-1": 4999})
	assert "MSRP: $49.99" in data["pieces_line"]


#============================================
def test_make_set_label_data_without_msrp() -> None:
	"""
	MSRP text is omitted when no cache value exists.
	"""
	set_dict = {
		"set_id": "123-1",
		"name": "Test Set",
		"category_name": "Theme",
		"year_released": 2020,
		"num_parts": 123,
		"theme_name": "Theme",
		"year": 2020,
		"set_img_url": "https://example.com/x.jpg",
	}
	data = reportlab_make_set_labels.make_set_label_data(set_dict, {})
	assert "MSRP" not in data["pieces_line"]


#============================================
def test_choose_set_name_size_longer_is_smaller() -> None:
	"""
	Very long names use smaller font sizes.
	"""
	short_name = "Small"
	long_name = "This Is A Very Long Set Name That Should Shrink"
	short_size = reportlab_make_set_labels.choose_set_name_size(short_name)
	long_size = reportlab_make_set_labels.choose_set_name_size(long_name)
	assert long_size < short_size
