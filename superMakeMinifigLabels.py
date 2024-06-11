#!/usr/bin/env python3

import os
import re
import sys
import time
import random
import shutil  # to save it locally
import requests  # to get image from the web
import bricklink_wrapper

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
def downloadImage(image_url, filename=None):
	if image_url is None:
		return None
	# Set up the image URL and filename
	if filename is None:
		filename = os.path.basename(image_url)
	if os.path.exists(filename):
		return filename
	time.sleep(random.random())
	# Open the url image, set stream to True, this will return the stream content.
	r = requests.get(image_url, stream=True)
	# Check if the image was retrieved successfully
	if r.status_code == 200:
		# Set decode_content value to True, otherwise the downloaded image file's size will be zero.
		r.raw.decode_content = True
		# Open a local file with wb ( write binary ) permission.
		with open(filename, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print('.. image successfully downloaded: ', filename)
	else:
		print(f"!! image couldn't be retrieved: {image_url}")
	return filename

#============================
#============================
#!/usr/bin/env python3

# Standard Library
import os
import re
import sys
import time
import random

#============================

def downloadImage(image_url: str, filename: str) -> None:
	"""
	Downloads an image from a given URL and saves it to the specified filename.

	Args:
		image_url (str): URL of the image to be downloaded.
		filename (str): Path where the image will be saved.
	"""
	# Dummy implementation for placeholder
	print(f"Downloading image from {image_url} to {filename}")
	time.sleep(random.random())

#============================

def makeLabel(minifig_dict: dict, price_dict: dict) -> str:
	"""
	Generates a LaTeX string for a given minifigure and its price details.

	Args:
		minifig_dict (dict): Dictionary containing minifigure details.
		price_dict (dict): Dictionary containing price details.

	Returns:
		str: LaTeX formatted string for the minifigure.
	"""
	print(minifig_dict)
	set_num = get_set_num(minifig_dict)
	minifig_id = minifig_dict.get('minifig_id')
	print(f'-----\nProcessing Minifig {minifig_id} from Set {set_num}')
	ensure_images_directory()
	filename = download_minifig_image(minifig_dict, minifig_id)
	minifig_name = format_minifig_name(minifig_dict.get('name'))
	name_fontsize = determine_fontsize(minifig_name)
	time_str = time.strftime("%b %Y", time.gmtime())
	latex_str = create_latex_string(minifig_id, set_num, minifig_dict, filename, name_fontsize, minifig_name, time_str, price_dict)
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

#============================

def ensure_images_directory() -> None:
	"""
	Creates an 'images' directory if it doesn't exist.
	"""
	if not os.path.isdir('images'):
		os.mkdir('images')

#============================

def download_minifig_image(minifig_dict: dict, minifig_id: str) -> str:
	"""
	Downloads the minifigure image and returns the filename.

	Args:
		minifig_dict (dict): Dictionary containing minifigure details.
		minifig_id (str): ID of the minifigure.

	Returns:
		str: Filename where the image is saved.
	"""
	filename = f"images/minifig_{minifig_id}.jpg"
	image_url = minifig_dict.get('image_url')
	image_url = 'https:' + image_url
	downloadImage(image_url, filename)
	return filename

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

def create_latex_string(minifig_id: str, set_num: str, minifig_dict: dict, filename: str, name_fontsize: str, name: str, time_str: str, price_dict: dict) -> str:
	"""
	Creates the LaTeX formatted string for the minifigure.

	Args:
		minifig_id (str): ID of the minifigure.
		set_num (str): Set number of the minifigure.
		minifig_dict (dict): Dictionary containing minifigure details.
		filename (str): Filename where the image is saved.
		name_fontsize (str): LaTeX font size command for the minifigure name.
		name (str): Formatted minifigure name.
		time_str (str): Current time formatted as a string.
		price_dict (dict): Dictionary containing price details.

	Returns:
		str: LaTeX formatted string for the minifigure.
	"""
	latex_str  = '\\begin{legocell}{' + filename + '}\n'
	latex_str += '\\textbf{\\color{DarkBlue}'
	if len(minifig_id) < 10:
		latex_str += '\\LARGE ' + str(minifig_id)
	else:
		latex_str += '\\large ' + str(minifig_id)
	latex_str += '} {\\sffamily\\tiny ' + time_str + '}\\par \n'
	latex_str += '\\vspace{-1pt} '
	if set_num is not None and len(set_num) > 3:
		latex_str += '{\\tiny \\> from set \\textbf{ ' + str(set_num) + ' } \\footnotesize (' + minifig_dict.get('year_released') + ')}\\par \n'
	else:
		latex_str += '{\\footnotesize \\> release year: ' + minifig_dict.get('year_released') + '}\\par \n'
	latex_str += '{\\sffamily' + name_fontsize + ' ' + name + '}\\par \n'
	latex_str += format_sales_info(price_dict)
	latex_str += format_list_info(price_dict)
	latex_str += '\\end{legocell}\n'
	return latex_str

#============================

def format_sales_info(price_dict: dict) -> str:
	"""
	Formats the sales information for the minifigure.

	Args:
		price_dict (dict): Dictionary containing price details.

	Returns:
		str: LaTeX formatted sales information.
	"""
	new_median_sale_price = float(price_dict['new_median_sale_price'])
	used_median_sale_price = float(price_dict['used_median_sale_price'])
	if new_median_sale_price > 0 or used_median_sale_price > 0:
		new_sale_qty = int(price_dict['new_sale_qty'])
		used_sale_qty = int(price_dict['used_sale_qty'])
		latex_str = '\\vspace{-3pt} {\\sffamily\\tiny sale: '
		if new_median_sale_price > 0 and used_median_sale_price > 0:
			latex_str += f'\${new_median_sale_price/100:.2f} new ({new_sale_qty}) / \${used_median_sale_price/100:.2f} used ({used_sale_qty})'
		elif new_sale_qty > 0 and new_median_sale_price > 0:
			latex_str += f'\${new_median_sale_price/100:.2f} new ({new_sale_qty})'
		elif used_sale_qty > 0 and used_median_sale_price > 0:
			latex_str += f'\${used_median_sale_price/100:.2f} used ({used_sale_qty})'
		latex_str += '}\\\\\n'
		return latex_str
	return ''

#============================

def format_list_info(price_dict: dict) -> str:
	"""
	Formats the listing information for the minifigure.

	Args:
		price_dict (dict): Dictionary containing price details.

	Returns:
		str: LaTeX formatted listing information.
	"""
	new_median_list_price = float(price_dict['new_median_list_price'])
	used_median_list_price = float(price_dict['used_median_list_price'])
	if new_median_list_price > 0 or used_median_list_price > 0:
		new_list_qty = int(price_dict['new_list_qty'])
		used_list_qty = int(price_dict['used_list_qty'])
		latex_str = '\\vspace{-3pt} {\\sffamily\\tiny list: '
		if new_median_list_price > 0 and used_median_list_price > 0:
			latex_str += f'\${new_median_list_price/100:.2f} new ({new_list_qty}) / \${used_median_list_price/100:.2f} used ({used_list_qty})'
		elif new_list_qty > 0 and new_median_list_price > 0:
			latex_str += f'\${new_median_list_price/100:.2f} new ({new_list_qty})'
		elif used_list_qty > 0 and used_median_list_price > 0:
			latex_str += f'\${used_median_list_price/100:.2f} used ({used_list_qty})'
		latex_str += '}\\\\\n'
		return latex_str
	return ''

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

	# Generate a timestamp for the output file
	timestamp = libbrick.make_timestamp()

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

		# Add additional data to minifig_data
		minifig_data['category_name'] = category_name
		minifig_data['set_id'] = setID

		# Fetch price data for the minifigure
		price_data = BLW.getMinifigPriceData(minifigID)
		total_data = {**minifig_data, **price_data}
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
	minifig_info_tree = sorted(minifig_info_tree, key=lambda item: int(item.get('minifig_id')))

	total_minifigs = len(minifig_info_tree)
	print(f"Found {total_minifigs} Minifigs to process")

	filename_root = os.path.splitext(minifigIDFile)[0]
	outfile = f"labels-{filename_root}.tex"
	pdffile = f"labels-{filename_root}.pdf"

	# Write the LaTeX labels to the output file
	with open(outfile, 'w') as f:
		f.write(latex_header)
		count = 0
		total_pages = total_minifigs // 30 + 1
		for minifig_dict in minifig_info_tree:
			minifigID = minifig_dict['minifig_id']
			price_dict = BLW.getMinifigPriceData(minifigID)
			count += 1
			label = makeLabel(minifig_dict, price_dict)
			f.write(label)
			if count % 5 == 0:
				f.write(f'% page {count//30 + 1} of {total_pages} --- gap line --- count {count} of {total_minifigs} ---\n')
		f.write(latex_footer)

	BLW.close()

	print(f'\n\nmogrify -verbose -trim images/minifig_*.jpg; \nxelatex {outfile}; \nopen {pdffile}')

#============================

if __name__ == "__main__":
	main()
