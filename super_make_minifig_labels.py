#!/usr/bin/env python3

import os
import re
import sys
import time
import random

import libbrick
import libbrick.image_cache
import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper

latex_header = r"""
\documentclass[letterpaper]{article}% Avery 18260
% https://www.avery.com/blank/labels/94200
\usepackage[top=0.5in, bottom=0.4in, left=0.28in, right=0.14in, noheadfoot]{geometry}
\usepackage{varwidth}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{fontspec}
\setsansfont[Ligatures=TeX]{PT Sans Narrow}
\definecolor{DarkBlue}{RGB}{0,0,100}

\newenvironment{legocell}[1]
{
	\begin{minipage}[c][0.98in][c]{2.625in}
	\centering
	% Avery 18260 described as 1in by 2 5/8in
	\varwidth{2.5in}
	\raggedright % but measures 2.75in wide
	\begin{minipage}[c]{0.5in}
		\includegraphics[width=0.45in,
			height=0.65in,
			keepaspectratio,]{#1}
	\end{minipage}
	\begin{minipage}[c]{1.9in}
	\raggedright
}
{
	\end{minipage}
	\endvarwidth
	\end{minipage}
	\allowbreak
	\ignorespaces
}

\parindent=0pt
\pagestyle{empty}

\begin{document}
\small
% set font size
"""

latex_footer = r"\end{document}\n"

#============================
#============================
def makeLabel(minifig_dict: dict, superset_count: int) -> str:
	"""
	Generates a LaTeX string for a given minifigure.

	Args:
		minifig_dict (dict): Dictionary containing minifigure details.
		superset_count (int): Number of sets the minifigure appears in.

	Returns:
		str: LaTeX formatted string for the minifigure.
	"""
	print(minifig_dict)
	set_num = get_set_num(minifig_dict)
	minifig_id = minifig_dict.get('minifig_id')
	print(f'-----\nProcessing Minifig {minifig_id} from Set {set_num}')
	filename = download_minifig_image(minifig_dict, minifig_id)
	minifig_name = format_minifig_name(minifig_dict.get('name'))
	name_fontsize = determine_fontsize(minifig_name)
	category_name = minifig_dict.get('category_name')
	latex_str = create_latex_string(
		minifig_id, minifig_dict, filename, name_fontsize, minifig_name,
		category_name, superset_count
	)
	print(f'{minifig_id} -- {set_num} ({minifig_dict.get("year_released")}) -- {minifig_dict.get("name")[:60]}')
	return latex_str
#============================

def get_set_num(minifig_dict: dict) -> str:
	"""
	Extracts the set number from the minifig dictionary.

	Args:
		minifig_dict (dict): Dictionary containing minifigure details.

	Returns:
		str: Set number.
	"""
	set_num = minifig_dict.get('set_num')
	if set_num is None:
		set_id = minifig_dict.get('set_id')
		if set_id is not None:
			set_num = set_id.split('-')[0]
	return set_num

def download_minifig_image(minifig_dict: dict, minifig_id: str) -> str:
	"""
	Downloads the minifigure image and returns the filename.

	Args:
		minifig_dict (dict): Dictionary containing minifigure details.
		minifig_id (str): ID of the minifigure.

	Returns:
		str: Filename where the image is saved.
	"""
	image_url = minifig_dict.get('image_url')
	return libbrick.image_cache.get_cached_image(image_url, 'minifig', minifig_id)

#============================

def format_minifig_name(name: str) -> str:
	"""
	Formats the minifigure name by removing unwanted characters and truncating if necessary.

	Args:
		name (str): Original minifigure name.

	Returns:
		str: Formatted minifigure name.
	"""
	name = name.replace('#', '')
	name = re.sub(r'\([^\)]+\)', '', name)
	if len(name) > 64:
		new_name = ''
		bits = name.split(' ')
		i = 0
		while len(new_name) < 58:
			new_name += bits[i] + ' '
			i += 1
		name = new_name.strip()
	return name

#============================

def determine_fontsize(name: str) -> str:
	"""
	Determines the LaTeX font size based on the length of the minifigure name.

	Args:
		name (str): Formatted minifigure name.

	Returns:
		str: LaTeX font size command.
	"""
	if len(name) < 18:
		return '\\normalsize'
	elif len(name) < 26:
		return '\\small'
	elif len(name) < 34:
		return '\\footnotesize'
	elif len(name) < 50:
		return '\\scriptsize'
	else:
		return '\\tiny'

#============================

def create_latex_string(minifig_id: str, minifig_dict: dict, filename: str,
		name_fontsize: str, name: str, category_name: str, superset_count: int) -> str:
	"""
	Creates the LaTeX formatted string for the minifigure.

	Args:
		minifig_id (str): ID of the minifigure.
		minifig_dict (dict): Dictionary containing minifigure details.
		filename (str): Filename where the image is saved.
		name_fontsize (str): LaTeX font size command for the minifigure name.
		name (str): Formatted minifigure name.
		category_name (str): Minifigure category name.
		superset_count (int): Number of sets the minifigure appears in.

	Returns:
		str: LaTeX formatted string for the minifigure.
	"""
	latex_str  = '\\begin{legocell}{' + filename + '}\n'
	latex_str += '\\textbf{\\color{DarkBlue}'
	if len(minifig_id) < 10:
		latex_str += '\\LARGE ' + str(minifig_id)
	else:
		latex_str += '\\large ' + str(minifig_id)
	latex_str += '}\\par \n'
	latex_str += '{\\sffamily' + name_fontsize + ' ' + name + '}\\par \n'
	latex_str += '\\vspace{-1pt} '
	latex_str += '{\\footnotesize \\> release year: ' + str(minifig_dict.get('year_released')) + '}\\par \n'
	if category_name is not None:
		latex_str += '{\\tiny \\> category: ' + str(category_name) + '}\\par \n'
	if superset_count is not None and superset_count > 0:
		latex_str += '{\\tiny \\> appears in ' + str(superset_count) + ' sets}\\par \n'
	latex_str += '\\end{legocell}\n'
	return latex_str

#============================
# Main Function
#============================
def main() -> None:
	"""
	Main function to process LEGO minifigure data from a given CSV file.
	Performs data lookup and label generation for each minifigure.
	"""
	# Check if the correct number of arguments is provided
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)

	# Get the input file name from the command line argument
	minifigIDFile = sys.argv[1]
	if not os.path.isfile(minifigIDFile):
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)

	# Read minifigure ID pairs from the input file
	minifigIDpairs = libbrick.read_minifigIDpairs_from_file(minifigIDFile)

	# Initialize the BrickLink wrapper
	BLW = bricklink_wrapper.BrickLink()
	line = 0

	minifig_info_tree = []
	for pair in minifigIDpairs:
		minifigID, setID = pair
		line += 1
		sys.stderr.write(".")
		try:
			# Fetch minifigure data from BrickLink
			minifig_data = BLW.getMinifigData(minifigID)
		except LookupError:
			continue

		try:
			# Fetch category name from BrickLink
			category_name = BLW.getCategoryNameFromMinifigID(minifigID)
		except LookupError:
			time.sleep(random.random())
			category_name = None

		try:
			superset_ids = BLW.getSupersetFromMinifigID(minifigID)
		except LookupError:
			time.sleep(random.random())
			superset_ids = None

		if superset_ids is None:
			superset_count = None
		else:
			superset_count = len(superset_ids)

		# Add additional data to minifig_data
		minifig_data['category_name'] = category_name
		minifig_data['set_id'] = setID
		minifig_data['superset_count'] = superset_count

		total_data = {**minifig_data}
		total_data['minifig_id'] = minifigID

		# Check and clean minifigure data
		if total_data.get('weight') is None:
			import pprint
			pprint.pprint(total_data)
			print('')
			print(total_data.keys())
			raise KeyError("Missing key: weight")

		if float(total_data['weight']) > 1000:
			print(f"TOO BIG: weight {total_data['weight']} skipping {total_data['no']} from set {total_data.get('set_num')}: {total_data['name'][:60]}")
			continue

		minifig_info_tree.append(total_data)

		# Save the cache every 50 lines
		if line % 50 == 0:
			BLW.save_cache()

	# Sort the minifigures by set ID
	minifig_info_tree = sorted(minifig_info_tree, key=lambda item: item.get('minifig_id'))

	total_minifigs = len(minifig_info_tree)
	print(f"Found {total_minifigs} Minifigs to process")

	filename_root = os.path.splitext(os.path.basename(minifigIDFile))[0]
	output_dir = libbrick.path_utils.get_output_dir()
	outfile = os.path.join(output_dir, f"labels-{filename_root}.tex")
	pdffile = os.path.join(output_dir, f"labels-{filename_root}.pdf")

	# Write the LaTeX labels to the output file
	with open(outfile, 'w') as f:
		f.write(latex_header)
		count = 0
		total_pages = total_minifigs // 30 + 1
		for minifig_dict in minifig_info_tree:
			minifigID = minifig_dict['minifig_id']
			count += 1
			label = makeLabel(minifig_dict, minifig_dict.get('superset_count'))
			f.write(label)
			if count % 5 == 0:
				f.write(f'% page {count//30 + 1} of {total_pages} --- gap line --- count {count} of {total_minifigs} ---\n')
		f.write(latex_footer)

	BLW.close()

	print(f'\n\nxelatex -output-directory "{output_dir}" "{outfile}"; \nopen "{pdffile}"')

#============================

if __name__ == "__main__":
	main()
