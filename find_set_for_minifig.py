#!/usr/bin/env python3

import os

import libbrick
import libbrick.minifig_sets
import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

if __name__ == '__main__':
	set_list = libbrick.read_setIDs_from_file('five_days_of_sets.csv')
	fig_list = libbrick.read_minifigIDpairs_from_file('filed.csv')
	#random.shuffle(fig_list)

	new_pairs = []
	blw = bricklink_wrapper.BrickLink()
	set_map = libbrick.minifig_sets.build_minifig_set_map(fig_list, set_list, blw)
	for minifigID, _ in fig_list:
		set_data = set_map.get(minifigID, {})
		superset_ids = set_data.get('superset_ids', [])
		valid_sets = set_data.get('valid_sets', [])
		print('{0}: {1} total sets: {2}'.format(minifigID, len(superset_ids), ', '.join(superset_ids)))
		print('{0}: {1} valid sets: {2}'.format(minifigID, len(valid_sets), ', '.join(valid_sets)))
		if len(valid_sets) == 1:
			pair = (minifigID, valid_sets[0])
			new_pairs.append(pair)
		elif len(valid_sets) > 1:
			fig_data = blw.getMinifigData(minifigID, verbose=False)
			print('\n{0}: {1}'.format(minifigID, fig_data.get('name')[:100]))
			for i, setID in enumerate(valid_sets):
				set_data = blw.getSetData(setID, verbose=False)
				print('{0}, {1}: {2}'.format(i, setID, set_data.get('name')))
			data = input('which number: ').strip()
			index = int(data)
			pair = (minifigID, valid_sets[index])
			new_pairs.append(pair)
			#print(data)
		else:
			pair = (minifigID, '')
			new_pairs.append(pair)

	output_dir = libbrick.path_utils.get_output_dir()
	f = open(os.path.join(output_dir, 'nov11-filed.csv'), 'w')
	new_pairs.sort()
	for pair in new_pairs:
		f.write('{0}\t{1}\n'.format(pair[0], pair[1]))
	f.close()

	blw.close()
	print(new_pairs)
