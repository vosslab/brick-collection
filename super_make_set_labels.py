#!/usr/bin/env python3

import os
import sys

import libbrick
import libbrick.image_cache
import libbrick.msrp_loader
import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as bricklink_wrapper
import libbrick.wrappers.rebrick_wrapper as rebrick_wrapper

latex_header = r"""
\documentclass[letterpaper]{article}% Avery 5163
\usepackage[top=0.5in, bottom=0.5in, left=0.16in, right=0.16in, noheadfoot]{geometry}
\usepackage{varwidth}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{fontspec}
\setsansfont[Ligatures=TeX]{PT Sans Narrow}
\definecolor{DarkBlue}{RGB}{0,0,100}

\newenvironment{legocell}[1]
{
	\begin{minipage}[c][2.0in][c]{4in}
	\centering
	% Avery 5163 described as 2in by 4in
	\varwidth{3.6in}
	\raggedright % but measures 4.125in wide
	\begin{minipage}[c]{1.3in}
		\includegraphics[width=1.29in,
			height=1.85in,
			keepaspectratio]{#1}
	\end{minipage}
	\begin{minipage}[c]{2.2in}
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
\Large
"""

latex_footer = r"\end{document}\n"

#============================

def makeLabel(set_dict: dict, msrp_cache: dict) -> str:
	"""
	Create a LaTeX formatted label for a LEGO set.

	Args:
		set_dict: Dictionary containing set information.
		msrp_cache: Dictionary containing MSRP cache values.

	Returns:
		Formatted LaTeX string for the label.
	"""
	set_id = set_dict.get('set_id')
	lego_id = int(set_id.split('-')[0])
	print(f'Processing Set {lego_id}')
	image_url = set_dict.get('set_img_url')
	filename = libbrick.image_cache.get_cached_image(image_url, 'set', set_id)

	set_name = set_dict.get('name').replace('#', '').replace(' & ', ' and ')

	latex_str  = (r'\begin{legocell}{' + filename + r'}' + '\n')
	latex_str += '    ' + (r'\textbf{' + str(lego_id) + r'}' + r'\\' + '\n')
	latex_str += '    ' + (r'{\sffamily\large ' + set_name + r'}' + r'\\' + '\n')
	latex_str += '    ' + (r'\textsc{\color{DarkBlue}\normalsize ' + set_dict.get('category_name') + r'}' + r'\\' + '\n')
	latex_str += '    ' + (r'(\textbf{' + str(set_dict.get('year_released')) + r'})' + r'\\' + '\n')
	latex_str += '    ' + (r'{\normalsize ' + str(set_dict.get('num_parts')) + r' pieces}' + r'\\' + '\n')

	msrp = msrp_cache.get(str(set_id))
	if msrp is not None and msrp > 0:
		latex_str += '    ' + (r'{\sffamily\scriptsize MSRP: $' + f'{msrp/100:.2f}' + r'}' + r'\\' + '\n')

	latex_str += r'\end{legocell}' + '\n'
	print(f'{lego_id} -- {set_dict.get("theme_name")} ({set_dict.get("year")}) -- {set_dict.get("name")}')

	return latex_str

#============================
#============================
def main():
	"""
	Main function to look up LEGO set data using BrickLink API and generate LaTeX file.
	"""
	if len(sys.argv) < 2:
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)
	setIDFile = sys.argv[1]
	if not os.path.isfile(setIDFile):
		print("usage: ./lookupLego.py <csv txt file with lego IDs>")
		sys.exit(1)

	setIDs = libbrick.read_setIDs_from_file(setIDFile)

	BLW = bricklink_wrapper.BrickLink()
	RBW = rebrick_wrapper.Rebrick()
	msrp_cache = libbrick.msrp_loader.load_msrp_cache()

	set_data_tree = []
	for setID in setIDs:
		if not '-' in setID:
			setID = str(setID) + "-1"
		set_data = BLW.getSetData(setID)
		rebrick_data = RBW.getSetData(setID)
		set_data.update(rebrick_data)
		extra_set_data = BLW.getSetDataDetails(setID)
		set_data.update(extra_set_data)
		set_data_tree.append(set_data)

	set_data_tree = sorted(set_data_tree, key=lambda item: int(item['set_id'].split('-')[0]))

	total_sets = len(set_data_tree)
	print(f"Found {total_sets} Lego Sets to process")

	filename_root = os.path.splitext(os.path.basename(setIDFile))[0]
	output_dir = libbrick.path_utils.get_output_dir()
	outfile = os.path.join(output_dir, f"labels-{filename_root}.tex")
	pdffile = os.path.join(output_dir, f"labels-{filename_root}.pdf")
	with open(outfile, 'w') as f:
		f.write(latex_header)
		count = 0
		total_pages = total_sets // 10 + 1
		for set_dict in set_data_tree:
			count += 1
			setID = set_dict.get('set_id')
			label = makeLabel(set_dict, msrp_cache)
			f.write(label)
			if count % 2 == 0:
				f.write(f'% page {count//10 + 1} of {total_pages} --- gap line --- count {count} of {total_sets} ---\n')
		f.write(latex_footer)
	BLW.close()
	print(f'xelatex -output-directory "{output_dir}" "{outfile}"; \nopen "{pdffile}"')
	sys.stderr.write("\n")


#============================
#============================
if __name__ == '__main__':
	main()
