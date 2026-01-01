#!/usr/bin/env python3

# Standard Library
import argparse
import csv
import os

# PIP3 modules
import yaml

# local repo modules
import libbrick
import libbrick.msrp_loader
import libbrick.path_utils

#============================
#============================
def _detect_delimiter(header_line: str) -> str:
	"""
	Detect the delimiter based on the header line.
	"""
	if ',' in header_line:
		return ','
	if '\t' in header_line:
		return '\t'
	return 'whitespace'

#============================
#============================
def _is_number(text: str) -> bool:
	"""
	Check if a string is a valid numeric value.
	"""
	if text == '.':
		return False
	allowed = set("0123456789.")
	if any(char not in allowed for char in text):
		return False
	if text.count('.') > 1:
		return False
	return True

#============================
#============================
def _parse_price(value: str, assume_cents: bool) -> int:
	"""
	Parse a price string into integer cents.
	"""
	if value is None:
		return None
	text = str(value).strip()
	if text == '':
		return None
	text = text.replace('$', '').replace(',', '')
	if text == '':
		return None
	if _is_number(text) is False:
		return None
	if assume_cents is True:
		return int(round(float(text)))
	if '.' in text:
		return int(round(float(text) * 100))
	return int(text) * 100

#============================
#============================
def _get_cache_path(cache_path: str = None) -> str:
	"""
	Return the MSRP cache path, defaulting to CACHE/msrp_cache.yml.
	"""
	if cache_path is not None:
		return cache_path
	git_root = libbrick.path_utils.get_git_root()
	if git_root is None:
		return os.path.join('CACHE', 'msrp_cache.yml')
	return os.path.join(git_root, 'CACHE', 'msrp_cache.yml')

#============================
#============================
def _pick_key(row: dict, candidates: list) -> str:
	"""
	Pick the first matching key from a row (case-insensitive).
	"""
	lower_row = {str(key).strip().lower(): key for key in row.keys() if key is not None}
	for candidate in candidates:
		key = lower_row.get(candidate)
		if key is not None:
			return key
	return None

#============================
#============================
def _read_rows(csv_path: str) -> list:
	"""
	Read rows from a CSV or whitespace-delimited file.
	"""
	if not os.path.isfile(csv_path):
		return []
	with open(csv_path, 'r', newline='') as f:
		header_line = f.readline()
		if header_line == '':
			return []
		delimiter = _detect_delimiter(header_line)
		f.seek(0)
		if delimiter == 'whitespace':
			lines = [line for line in f if line.strip() and not line.lstrip().startswith('#')]
			if not lines:
				return []
			headers = lines[0].strip().split()
			rows = []
			for line in lines[1:]:
				parts = line.strip().split()
				if len(parts) < len(headers):
					parts += [''] * (len(headers) - len(parts))
				row = dict(zip(headers, parts))
				rows.append(row)
			return rows
		reader = csv.DictReader(f, delimiter=delimiter)
		rows = []
		for row in reader:
			if row is None:
				continue
			values = [str(value).strip() for value in row.values() if value is not None]
			if not values:
				continue
			if values[0].startswith('#'):
				continue
			rows.append(row)
		return rows

#============================
#============================
def update_msrp_cache(csv_path: str, cache_path: str, assume_cents: bool,
		dry_run: bool) -> None:
	"""
	Update the MSRP cache from a CSV with Number and Retail columns.
	"""
	rows = _read_rows(csv_path)
	if not rows:
		print(f"Error: No rows found in {csv_path}")
		return
	cache_path = _get_cache_path(cache_path)
	cache_data = libbrick.msrp_loader.load_msrp_cache(cache_path)
	if isinstance(cache_data, dict) is False:
		cache_data = {}
	number_keys = ['number', 'set', 'set_id', 'setid', 'id']
	retail_keys = ['retail', 'msrp', 'price']
	added = 0
	updated = 0
	skipped = 0
	for row in rows:
		number_key = _pick_key(row, number_keys)
		retail_key = _pick_key(row, retail_keys)
		if number_key is None or retail_key is None:
			skipped += 1
			continue
		set_id = libbrick.processSetID(row.get(number_key))
		if set_id is None:
			print(f"Skipping invalid set ID: {row.get(number_key)}")
			skipped += 1
			continue
		price_cents = _parse_price(row.get(retail_key), assume_cents)
		if price_cents is None:
			print(f"Skipping invalid retail price for {set_id}: {row.get(retail_key)}")
			skipped += 1
			continue
		existing = cache_data.get(set_id)
		if existing not in (None, 0):
			skipped += 1
			continue
		if existing is None:
			added += 1
		else:
			updated += 1
		cache_data[set_id] = price_cents
	if dry_run is True:
		print("Dry run: no cache updates written")
		print(f"Added {added}, updated {updated}, skipped {skipped}")
		return
	cache_dir = os.path.dirname(cache_path)
	if cache_dir and os.path.isdir(cache_dir) is False:
		os.makedirs(cache_dir, exist_ok=True)
	with open(cache_path, 'w') as f:
		yaml.safe_dump(cache_data, f, sort_keys=True, default_flow_style=False)
	print(f"Wrote MSRP cache to {cache_path}")
	print(f"Added {added}, updated {updated}, skipped {skipped}")

#============================
#============================
def main():
	parser = argparse.ArgumentParser(
		description="Update CACHE/msrp_cache.yml from a CSV with Number and Retail columns."
	)
	parser.add_argument('csvfile', help="Input CSV file with Number and Retail columns")
	parser.add_argument('--cache', dest='cache_path', default=None,
		help="Optional path to msrp_cache.yml (default: CACHE/msrp_cache.yml)")
	parser.add_argument('--assume-cents', dest='assume_cents', action='store_true',
		help="Treat retail values as cents instead of dollars")
	parser.add_argument('--dry-run', dest='dry_run', action='store_true',
		help="Show changes without writing the cache file")
	args = parser.parse_args()

	update_msrp_cache(
		args.csvfile,
		args.cache_path,
		args.assume_cents,
		args.dry_run
	)

#============================
#============================
if __name__ == '__main__':
	main()
