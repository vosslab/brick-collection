# Standard Library
import time
import random

#============================
#============================
def build_minifig_set_map(fig_list: list, set_list: list, blw) -> dict:
	"""
	Build a mapping of minifig IDs to their superset IDs and valid sets.

	Args:
		fig_list (list): List of (minifig_id, set_id) pairs.
		set_list (list): List of valid set IDs to filter against.
		blw: BrickLink wrapper instance.

	Returns:
		dict: Mapping of minifig_id to dict with keys:
			- superset_ids
			- valid_sets
	"""
	if fig_list is None:
		return {}
	if set_list is None:
		set_list = []
	set_lookup = set(set_list)
	result = {}
	for minifig_id, _ in fig_list:
		try:
			superset_ids = blw.getSupersetFromMinifigID(minifig_id)
		except LookupError:
			time.sleep(random.random())
			superset_ids = []
		valid_sets = []
		for set_id in superset_ids:
			if set_id in set_lookup:
				valid_sets.append(set_id)
		result[minifig_id] = {
			'superset_ids': superset_ids,
			'valid_sets': valid_sets,
		}
	return result
