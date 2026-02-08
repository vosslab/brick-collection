import libbrick.reportlab_label_utils


#============================================
def _assert_grid_valid(config: libbrick.reportlab_label_utils.ImpositionConfig) -> None:
	"""
	Common geometry assertions for a layout config.
	"""
	libbrick.reportlab_label_utils.validate_config(config)
	for row in range(config.rows):
		for col in range(config.columns):
			x0, y0, x1, y1 = libbrick.reportlab_label_utils.slot_bbox(config, row, col)
			assert x1 > x0
			assert y1 > y0
			cx0, cy0, cx1, cy1 = libbrick.reportlab_label_utils.content_bbox(config, row, col)
			assert cx1 > cx0
			assert cy1 > cy0
	for col in range(config.columns - 1):
		left = libbrick.reportlab_label_utils.slot_bbox(config, 0, col)
		right = libbrick.reportlab_label_utils.slot_bbox(config, 0, col + 1)
		assert right[0] >= left[2] - 0.001
	for row in range(config.rows - 1):
		upper = libbrick.reportlab_label_utils.slot_bbox(config, row, 0)
		lower = libbrick.reportlab_label_utils.slot_bbox(config, row + 1, 0)
		assert lower[3] <= upper[1] + 0.001


#============================================
def test_avery_5163_geometry() -> None:
	"""
	Avery 5163 slots are on-page and non-overlapping.
	"""
	_assert_grid_valid(libbrick.reportlab_label_utils.AVERY_5163_SET_CONFIG)


#============================================
def test_avery_18260_geometry() -> None:
	"""
	Avery 18260 slots are on-page and non-overlapping.
	"""
	_assert_grid_valid(libbrick.reportlab_label_utils.AVERY_18260_MINIFIG_CONFIG)
