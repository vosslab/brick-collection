"""
Shared CSV export helpers for LEGO pricing pipelines.
"""

FAVORITE_COLUMNS = [
	'total quantity', 'item_id', 'color_name', 'name',
	'category name', 'lot value', 'sale price',
	'total lot mass', 'total lot volume', 'valid_image_url',
]

#============================================
def format_number_human(value):
	"""
	Format a numeric value for human-readable CSV export.

	Avoids scientific notation for all finite floats.
	Strips trailing zeros and decimal points.

	Args:
		value: int, float, or any value to be formatted.

	Returns:
		str: Formatted value, or empty string if value is None or a non-numeric type.
	"""
	if value is None:
		return ''
	if value == 0:
		return '0'
	if isinstance(value, int):
		return str(value)
	if isinstance(value, float):
		# Use different precision based on magnitude
		if 1e-3 <= abs(value) < 1e9:
			formatted = f'{value:.3f}'
		else:
			formatted = f'{value:.6f}'
		# Strip trailing zeros and decimal point
		formatted = formatted.rstrip('0').rstrip('.')
		return formatted
	return ''

#============================================
def process_value(value):
	"""
	Process a single value based on its type for CSV output.

	Cleans strings and delegates float formatting to format_number_human.
	Truncates to 70 chars unless the string is a URL.

	Args:
		value: The data value to be processed.

	Returns:
		str: Processed value ready for CSV output.
	"""
	if isinstance(value, str):
		# Replacing problematic characters
		value = value.replace('\n', ' ')
		value = value.replace('\t', ' ')
		value = value.replace(',', ' ')
		value = value.replace('  ', ' ')
		# Truncating string if longer than 70 characters; do not truncate URLs
		if not value.startswith(('http://', 'https://')):
			value = value[:70]
	elif isinstance(value, float):
		# Delegate float formatting to format_number_human
		value = format_number_human(value)
	return value

#============================================
def process_row(data: dict, allkeys: list) -> list:
	"""
	Process the given data and return a row ready for CSV.

	Args:
		data (dict): The data dictionary containing fields.
		allkeys (list): List of keys to determine column order.

	Returns:
		list: Processed row values.
	"""
	row = []
	for key in allkeys:
		value = data.get(key, '')
		row.append(process_value(value))
	return row

#============================================
def write_csv_row(writer, data: dict, allkeys: list) -> None:
	"""
	Write a single data row to the CSV writer.

	Args:
		writer: csv.writer object.
		data (dict): The data dictionary for this row.
		allkeys (list): Column key ordering.
	"""
	row = process_row(data, allkeys)
	writer.writerow(row)

#============================================
def build_column_order(data: dict, favorites: list = FAVORITE_COLUMNS) -> list:
	"""
	Build the column order for CSV export.

	Returns favorites first, followed by remaining keys in sorted order.

	Args:
		data (dict): The data dictionary.
		favorites (list): Preferred column order (default FAVORITE_COLUMNS).

	Returns:
		list: Ordered list of column keys.
	"""
	datakeys = sorted(data.keys())
	allkeys = favorites + [key for key in datakeys if key not in favorites]
	return allkeys

#============================================
def clean_data_for_export(data: dict) -> dict:
	"""
	Remove unused/legacy fields from data before CSV export.

	Removes 'image_url', 'thumbnail_url', and any key starting with 'used_'.

	Args:
		data (dict): The raw data dictionary.

	Returns:
		dict: The cleaned data dictionary (modified in place).
	"""
	data.pop('image_url', None)
	data.pop('thumbnail_url', None)
	# Remove all used_ prefix keys
	for key in list(data.keys()):
		if key.startswith('used_'):
			data.pop(key, None)
	return data

#============================================
def build_image_urls(element_id, part_id, color_id, item_type, item_id) -> dict:
	"""
	Build a dict of image URLs for a LEGO item.

	Supports PART and MINIFIG item types. Returns empty strings for
	missing or invalid inputs.

	Args:
		element_id: LEGO element ID (for LEGO and Rebrickable URLs).
		part_id: BrickLink part ID (for PART type items).
		color_id: BrickLink color ID (for PART type items).
		item_type: 'PART' or 'MINIFIG'.
		item_id: BrickLink item ID (for MINIFIG type items).

	Returns:
		dict with keys: lego_image_url, rebrickable_image_url, bricklink_image_url.
	"""
	urls = {
		'lego_image_url': '',
		'rebrickable_image_url': '',
		'bricklink_image_url': '',
	}

	# LEGO and Rebrickable URLs require element_id
	if element_id:
		urls['lego_image_url'] = (
			f'https://www.lego.com/cdn/product-assets/element.img.lod5photo.192x192/{element_id}.jpg'
		)
		urls['rebrickable_image_url'] = (
			f'https://cdn.rebrickable.com/media/thumbs/parts/elements/{element_id}.jpg/250x250p.jpg'
		)

	# BrickLink URL depends on item_type
	if item_type == 'PART' and part_id and color_id:
		urls['bricklink_image_url'] = (
			f'https://img.bricklink.com/ItemImage/PN/{color_id}/{part_id}.png'
		)
	elif item_type == 'MINIFIG' and item_id:
		urls['bricklink_image_url'] = (
			f'https://img.bricklink.com/ItemImage/MN/0/{item_id}.original.png'
		)

	return urls

#============================================
def pick_valid_image_url(blw, urls_in_priority_order: list) -> str:
	"""
	Pick the first valid image URL from a priority-ordered list.

	Iterates through the provided URLs, skips falsy/empty entries, and
	returns the first URL where blw.image_exists(url) is truthy.

	Args:
		blw: BrickLink wrapper instance with image_exists(url) method.
		urls_in_priority_order (list): URLs to check in priority order.

	Returns:
		str: First valid URL, or empty string if none are valid.
	"""
	for url in urls_in_priority_order:
		if not url:
			continue
		if blw.image_exists(url):
			return url
	return ''
