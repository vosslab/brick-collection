#!/usr/bin/env python3

import os
import sys
import time
import random
import shutil
import requests
import bricklink_wrapper

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

def downloadImage(image_url: str, filename: str = None) -> str:
	"""
	Download an image from a given URL and save it locally.

	Args:
		image_url: URL of the image to download.
		filename: Optional; local filename to save the image as.

	Returns:
		Filename of the saved image.
	"""
	if image_url is None:
		return None
	if filename is None:
		filename = os.path.basename(image_url)
	if os.path.exists(filename):
		return filename
	time.sleep(random.random())
	r = requests.get(image_url, stream=True)
	if r.status_code == 200:
		r.raw.decode_content = True
		with open(filename, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print(f'.. image successfully downloaded: {filename}')
	else:
		print(f"!! image couldn't be retrieved: {image_url}")
	return filename

def format_price_info(new_price: float, new_qty: int, used_price: float, used_qty: int) -> str:
	"""
	Format the price information for the LaTeX label.

	Args:
		new_price: Median sale price for new sets.
		new_qty: Quantity of new sets available.
		used_price: Median sale price for used sets.
		used_qty: Quantity of used sets available.

	Returns:
		Formatted LaTeX string for the price information.
	"""
	price_info = r'{\sffamily\scriptsize sale: '
	if new_price > 0 and used_price > 0:
		price_info += f'\\${new_price/100:.2f} new ({new_qty}) / \\${used_price/100:.2f} used ({used_qty})'
	elif new_qty > 0 and new_price > 0:
		price_info += f'\\${new_price/100:.2f} new ({new_qty})'
	elif used_qty > 0 and used_price > 0:
		price_info += f'\\${used_price/100:.2f} used ({used_qty})'
	price_info += r'}'
	return price_info

def format_list_info(new_list_price: float, new_list_qty: int, used_list_price: float, used_list_qty: int) -> str:
	"""
	Format the list price information for the LaTeX label.

	Args:
		new_list_price: Median list price for new sets.
		new_list_qty: Quantity of new sets listed.
		used_list_price: Median list price for used sets.
		used_list_qty: Quantity of used sets listed.

	Returns:
		Formatted LaTeX string for the list price information.
	"""
	list_info = r'{\sffamily\scriptsize list: '
	if new_list_price > 0 and used_list_price > 0:
		list_info += f'\\${new_list_price/100:.2f} new ({new_list_qty}) / \\${used_list_price/100:.2f} used ({used_list_qty})'
	elif new_list_qty > 0 and new_list_price > 0:
		list_info += f'\\${new_list_price/100:.2f} new ({new_list_qty})'
	elif used_list_qty > 0 and used_list_price > 0:
		list_info += f'\\${used_list_price/100:.2f} used ({used_list_qty})'
	list_info += r'}'
	return list_info


def makeLabel(set_dict: dict, price_dict: dict) -> str:
	"""
	Create a LaTeX formatted label for a LEGO set.

	Args:
		set_dict: Dictionary containing set information.
		price_dict: Dictionary containing price information.

	Returns:
		Formatted LaTeX string for the label.
	"""
	set_id = set_dict.get('set_id')
	lego_id = int(set_id.split('-')[0])
	print(f'Processing Set {lego_id}')
	if not os.path.isdir('images'):
		os.mkdir('images')
	filename = f"images/set_{set_id}.jpg"
	image_url = set_dict.get('set_img_url')
	downloadImage(image_url, filename)

	set_name = set_dict.get('name').replace('#', '').replace(' & ', ' and ')

	latex_str  = (r'\begin{legocell}{' + filename + r'}' + '\n')
	latex_str += '    ' + (r'\textbf{' + str(lego_id) + r'}' + r'\\' + '\n')
	latex_str += '    ' + (r'{\sffamily\large ' + set_name + r'}' + r'\\' + '\n')
	latex_str += '    ' + (r'\textsc{\color{DarkBlue}\normalsize ' + set_dict.get('category_name') + r'}' + r'\\' + '\n')
	latex_str += '    ' + (r'(\textbf{' + set_dict.get('year_released') + r'})' + r'\\' + '\n')
	latex_str += '    ' + (r'{\normalsize ' + set_dict.get('num_parts') + r' pieces}' + r'\\' + '\n')

	latex_str += '    ' + format_price_info(
		float(price_dict['new_median_sale_price']),
		int(price_dict['new_sale_qty']),
		float(price_dict['used_median_sale_price']),
		int(price_dict['used_sale_qty'])
	).replace(r'\\', r'\\\\') + '\n'

	latex_str += '    ' + format_list_info(
		float(price_dict['new_median_list_price']),
		int(price_dict['new_list_qty']),
		float(price_dict['used_median_list_price']),
		int(price_dict['used_list_qty'])
	).replace(r'\\', r'\\\\') + '\n'

	latex_str += r'\end{legocell}' + '\n'
	print(f'{lego_id} -- {set_dict.get("theme_name")} ({set_dict.get("year")}) -- {set_dict.get("name")}')

	return latex_str




def main():
	if len(sys.argv) < 2:
		print("usage: ./makeLabels.py <rebrick csv txt file>")
		sys.exit(1)
	legoidFile = sys.argv[1]
	if not os.path.isfile(legoidFile):
		print("usage: ./makeLabels.py <rebrick csv txt file>")
		sys.exit(1)

	legoIDs = []
	with open(legoidFile, "r") as f:
		line_count = 0
		keys = None
		set_info_tree = []
		for line in f:
			sline = line.strip()
			line_count += 1
			if line_count == 1:
				keys = sline.split('\t')
				print(keys)
				continue
			set_dict = {}
			values = sline.split('\t')
			for index, val in enumerate(values):
				key = keys[index]
				set_dict[key] = val
			set_info_tree.append(set_dict)
	set_info_tree = sorted(set_info_tree, key=lambda item: int(item['set_id'].split('-')[0]))

	total_sets = len(set_info_tree)
	print(f"Found {total_sets} Lego Sets to process")

	filename_root = os.path.splitext(legoidFile)[0]
	outfile = f"labels-{filename_root}.tex"
	pdffile = f"labels-{filename_root}.pdf"
	with open(outfile, 'w') as f:
		f.write(latex_header)
		count = 0
		total_pages = total_sets // 10 + 1
		BLwrap = bricklink_wrapper.BrickLink()
		for set_dict in set_info_tree:
			count += 1
			setID = set_dict['set_id']
			legoID = int(setID.split('-')[0])
			price_dict = BLwrap.getSetPriceData(setID)
			label = makeLabel(set_dict, price_dict)
			f.write(label)
			if count % 2 == 0:
				f.write(f'% page {count//10 + 1} of {total_pages} --- gap line --- count {count} of {total_sets} ---\n')
		f.write(latex_footer)
	BLwrap.close()
	print(f'mogrify -verbose -trim images/set_*.jpg; \nxelatex {outfile}; \nopen {pdffile}')

if __name__ == '__main__':
	main()

