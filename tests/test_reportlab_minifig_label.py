import reportlab_make_minifig_labels


#============================================
def test_make_minifig_label_data_contains_expected_fields() -> None:
	"""
	Derived minifig label data includes optional fields.
	"""
	minifig_dict = {
		"minifig_id": "fig1",
		"name": "Test Name (Variant)",
		"year_released": 2020,
		"category_name": "Star Wars",
		"set_id": "1234-1",
	}
	data = reportlab_make_minifig_labels.make_minifig_label_data(minifig_dict, 3)
	assert data["minifig_id"] == "fig1"
	assert data["year_released"] == "2020"
	assert data["category_name"] == "Star Wars"
	assert data["superset_count"] == 3
	assert "(" not in data["name"]


#============================================
def test_determine_name_size_longer_is_smaller() -> None:
	"""
	Longer minifig names should map to smaller fonts.
	"""
	short_size = reportlab_make_minifig_labels.determine_name_size("Small")
	long_size = reportlab_make_minifig_labels.determine_name_size(
		"This Is A Very Long Minifig Name That Should Be Smaller"
	)
	assert long_size < short_size
