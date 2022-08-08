#!/usr/bin/env python

import os
import sys
import time
import random
import string
import shutil # to save it locally
import requests # to get image from the web

latex_header = """
\\documentclass[letterpaper]{article}% Avery 5163
\\usepackage[top=0.5in, bottom=0.5in, left=0.16in, right=0.16in, noheadfoot]{geometry}
\\usepackage{varwidth}
\\usepackage{graphicx}
\\usepackage{xcolor}
\\usepackage{fontspec}
\\setsansfont[Ligatures=TeX]{Liberation Sans Narrow}
\definecolor{DarkBlue}{RGB}{0,0,100}

\\newenvironment{legocell}[1]
{
	\\begin{minipage}[c][2.0in][c]{4in}
	\\centering
	% Avery 5163 described as 2in by 4in
	\\varwidth{3.6in}
	\\raggedright % but measures 4.125in wide
	\\begin{minipage}[c]{1.3in}
		\\includegraphics[width=1.29in,
			height=1.85in,
			keepaspectratio,]{#1}
	\\end{minipage}
	\\begin{minipage}[c]{2.2in}
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
\\Large
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
		print('Image sucessfully Downloaded: ', filename)
	else:
		print('Image Couldn\'t be retreived: '+image_url)
	return filename

#============================
#============================
def makeLabel(set_dict):
	"""
	\begin{legocell}{set_10745-1.jpg}
	Lego ID --- Title\\
	Theme (Year)
	\end{legocell}
	"""
	set_id = set_dict.get('set_num')
	lego_id = int(set_id.split('-')[0])
	print('Processing Set {0}'.format(lego_id))
	filename = "images/set_{0}.jpg".format(set_id)
	image_url = set_dict.get('set_img_url')
	downloadImage(image_url, filename)

	latex_str  = ('\\begin{legocell}{'
		+filename
		+'}\n')
	latex_str += ('\\textbf{'
		+str(lego_id)
		+'}\\\\\n')
	latex_str += ('{\\sffamily\\large '
		+set_dict.get('name')
		+'}\\\\\n')
	latex_str += ('\\textsc{\\color{DarkBlue}\\normalsize '
		+set_dict.get('theme_name')
		+'}\\\\\n')
	latex_str += ('(\\textbf{'
		+set_dict.get('year')
		+'})\\\\\n')
	latex_str += ('{\\normalsize '
		+set_dict.get('num_parts')
		+' pieces}\\\\\n')
	latex_str += '\\end{legocell}\n'
	#print(latex_str)
	print('{0} -- {1} ({2})-- {3}'.format(
		lego_id, set_dict.get('theme_name'),
		set_dict.get('year'), set_dict.get('name')))

	return latex_str

#============================
#============================
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("usage: ./makeLabels.py <rebrick csv txt file>")
		sys.exit(1)
	legoidFile = sys.argv[1]
	if not os.path.isfile(legoidFile):
		print("usage: ./makeLabels.py <rebrick csv txt file>")
		sys.exit(1)

	legoIDs = []
	f = open(legoidFile, "r")
	line_count = 0
	keys = None
	set_info_tree = []
	for line in f:
		sline = line.strip()
		line_count += 1
		if line_count == 1:
			#setup keys
			keys = sline.split('\t')
			print(keys)
			continue
		set_dict = {}
		values = sline.split('\t')
		for index, val in enumerate(values):
			key = keys[index]
			set_dict[key] = val
		set_info_tree.append(set_dict)
	f.close()
	set_info_tree = sorted(set_info_tree, key = lambda item: int(item['set_num'][:-2]))

	total_sets = len(set_info_tree)
	print("Found {0} Lego Sets to process".format(total_sets))
	#random.shuffle(set_info_tree)

	filename_root = os.path.splitext(legoidFile)[0]
	outfile = filename_root + '.tex'
	pdffile = filename_root + '.pdf'
	f = open(outfile, 'w')
	f.write(latex_header)
	count = 0
	total_pages = total_sets // 10 + 1
	for set_dict in set_info_tree:
		count += 1
		label = makeLabel(set_dict)
		f.write(label)
		if count % 2 == 0:
			f.write('% page {0} of {1} --- gap line --- count {2} of {3} ---\n'.format(
				count//10 + 1, total_pages, count, total_sets))
	f.write(latex_footer)
	f.close()
	print('mogrify -verbose -trim images/set_*.jpg; \nxelatex {0}; open {1}'.format(outfile, pdffile))
