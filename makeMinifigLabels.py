#!/usr/bin/env python3

import os
import sys
import time
import random
import string
import shutil # to save it locally
import requests # to get image from the web
import bricklink_wrapper

latex_header = """
\\documentclass[letterpaper]{article}% Avery 18260
% https://www.avery.com/blank/labels/94200
\\usepackage[top=0.5in, bottom=0.4in, left=0.28in, right=0.14in, noheadfoot]{geometry}
\\usepackage{varwidth}
\\usepackage{graphicx}
\\usepackage{xcolor}
\\usepackage{fontspec}
\\setsansfont[Ligatures=TeX]{Liberation Sans Narrow}
\definecolor{DarkBlue}{RGB}{0,0,100}

\\newenvironment{legocell}[1]
{
	\\begin{minipage}[c][0.98in][c]{2.625in}
	\\centering
	% Avery 18260 described as 1in by 2 5/8in
	\\varwidth{2.5in}
	\\raggedright % but measures 2.75in wide
	\\begin{minipage}[c]{0.7in}
		\\includegraphics[width=0.65in,
			height=0.65in,
			keepaspectratio,]{#1}
	\\end{minipage}
	\\begin{minipage}[c]{1.7in}
	\\raggedright
}
{
	\\end{minipage}
	\\endvarwidth
	\\end{minipage}
	\\allowbreak
	\\ignorespaces
}

\\parindent=0pt
\\pagestyle{empty}

\\begin{document}
\\small
% set font size
"""

latex_footer = "\\end{document}\n"

#============================
#============================
def downloadImage(image_url, filename=None):
	if image_url is None:
		return None
	## Set up the image URL and filename
	if filename is None:
		filename = os.path.basename(image_url)
	if os.path.exists(filename):
		return filename
	time.sleep(random.random())
	# Open the url image, set stream to True, this will return the stream content.
	r = requests.get(image_url, stream = True)
	# Check if the image was retrieved successfully
	if r.status_code == 200:
		# Set decode_content value to True, otherwise the downloaded image file's size will be zero.
		r.raw.decode_content = True
		# Open a local file with wb ( write binary ) permission.
		with open(filename,'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print('.. image sucessfully downloaded: ', filename)
	else:
		print('!! image couldn\'t be retreived: '+image_url)
	return filename

#============================
#============================
def makeLabel(minifig_dict, price_dict):
	"""
	\begin{legocell}{minifig_sw0094.jpg}
	Minifig ID from set Lego ID (Year)\\
	Name
	Sales / Avg Price
	\end{legocell}
	"""
	print(minifig_dict)
	set_num = minifig_dict.get('set_num')
	minifig_id = minifig_dict.get('minifig_id')
	print('-----\nProcessing Minifig {0} from Set {0}'.format(minifig_id, set_num))
	filename = "images/minifig_{0}.jpg".format(minifig_id)
	image_url = minifig_dict.get('image_url')
	image_url = 'https:' + image_url
	downloadImage(image_url, filename)

	minifig_name = minifig_dict.get('name')
	minifig_name = minifig_name.replace('#', '')
	if len(minifig_name) > 100:
		new_name = ''
		bits = minifig_name.split(' ')
		i = 0
		while len(new_name) < 90:
			new_name += bits[i] + ' '
			i += 1
		minifig_name = new_name
	new_median_price = float(price_dict['new_median_price'])
	used_median_price = float(price_dict['used_median_price'])
	latex_str  = ('\\begin{legocell}{'
		+filename
		+'}\n')
	latex_str += ('\\textbf{\\color{DarkBlue}\\Large '
		+str(minifig_id)
		+'}\\\\\n')
	latex_str += ('from set \\textbf{\\large'
		+str(set_num)
		+ '} ('
		+minifig_dict.get('year_released')
		+')\\\\\n')
	latex_str += ('{\\sffamily\\scriptsize '
		+minifig_name
		+'}\\\\\n')
	latex_str += '{\\scriptsize '
	latex_str += '${0:.2f} new / ${1:.2f} used '.format(new_median_price, used_median_price)
	latex_str += '}\\\\\n'
	latex_str += '\\end{legocell}\n'
	#print(latex_str)
	print('{0} -- {1} ({2}) -- {3}'.format(
		minifig_id, set_num,
		minifig_dict.get('year_released'), minifig_dict.get('name')[:60]))

	return latex_str

#============================
#============================
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("usage: ./makeLabels.py <bricklink minifig csv txt file>")
		sys.exit(1)
	minifigidFile = sys.argv[1]
	if not os.path.isfile(minifigidFile):
		print("usage: ./makeLabels.py <bricklink minifig csv txt file>")
		sys.exit(1)

	if 'minifig' not in minifigidFile.lower():
		print("WARNING: this program takes minifig data, not set data")
		time.sleep(1)

	minifigIDs = []
	f = open(minifigidFile, "r")
	line_count = 0
	keys = None
	minifig_info_tree = []
	for line in f:
		sline = line.strip()
		line_count += 1
		if line_count == 1:
			#setup keys
			keys = sline.split('\t')
			print(keys)
			continue
		minifig_dict = {}
		values = sline.split('\t')
		for index, val in enumerate(values):
			key = keys[index]
			minifig_dict[key] = val
		if float(minifig_dict['weight']) > 10e6:
			print("TOO BIG: weight {3} skipping {0} from set {1}: {2}".format(
				minifig_dict['no'], minifig_dict['set_num'], minifig_dict['name'][:60], minifig_dict['weight']))
			continue
		minifig_info_tree.append(minifig_dict)
	f.close()
	minifig_info_tree = sorted(minifig_info_tree, key = lambda item: item['no'])
	minifig_info_tree = sorted(minifig_info_tree, key = lambda item: int(item['set_num']))

	total_minifigs = len(minifig_info_tree)
	print("Found {0} Minifigs to process".format(total_minifigs))

	filename_root = os.path.splitext(minifigidFile)[0]
	outfile = "labels-" + filename_root + '.tex'
	pdffile = "labels-" + filename_root + '.pdf'
	f = open(outfile, 'w')
	f.write(latex_header)
	count = 0
	total_pages = total_minifigs // 30 + 1
	BLwrap = bricklink_wrapper.BrickLink()
	for minifig_dict in minifig_info_tree:
		minifigID = minifig_dict['minifig_id']
		price_dict = BLwrap.getMinifigsPriceData(minifigID)
		count += 1
		label = makeLabel(minifig_dict, price_dict)
		f.write(label)
		if count % 5 == 0:
			f.write('% page {0} of {1} --- gap line --- count {2} of {3} ---\n'.format(
				count//30 + 1, total_pages, count, total_minifigs))
	f.write(latex_footer)
	f.close()
	print('\n\nmogrify -verbose -trim images/minifig_*.jpg; \nxelatex {0}; open {1}'.format(outfile, pdffile))
