import superMakeMinifigLabels

#============================
#============================
def test_create_latex_string_contains_fields():
	"""
	Includes all expected minifig fields in the label output.
	"""
	minifig_dict = {
		'year_released': 2020,
	}
	result = superMakeMinifigLabels.create_latex_string(
		'fig1',
		minifig_dict,
		'images/processed/minifig_fig1.png',
		'\\small',
		'Test Name',
		'Star Wars',
		3,
	)
	assert 'fig1' in result
	assert 'Test Name' in result
	assert 'release year: 2020' in result
	assert 'category: Star Wars' in result
	assert 'appears in 3 sets' in result
