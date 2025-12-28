# Standard Library
import os
import time
import random
import shutil
import subprocess

# PIP3 modules
import requests

# local repo modules
import libbrick.path_utils

#============================
#============================
def ensure_images_directory(base_dir: str) -> None:
	"""
	Creates an 'images' directory with raw and processed subfolders.
	"""
	if not os.path.isdir(base_dir):
		os.mkdir(base_dir)
	for subdir in ('raw', 'processed'):
		subdir_path = os.path.join(base_dir, subdir)
		if not os.path.isdir(subdir_path):
			os.mkdir(subdir_path)

#============================

def ensure_image_tools_installed() -> None:
	"""
	Ensures required image tools are installed and available in PATH.
	"""
	if shutil.which('rembg') is None:
		raise FileNotFoundError("rembg not found in PATH")
	if shutil.which('mogrify') is None:
		raise FileNotFoundError("mogrify not found in PATH")

#============================

def normalize_image_url(image_url: str) -> str:
	"""
	Ensure image URLs use https when missing a scheme.
	"""
	if image_url is None:
		return None
	if image_url.startswith('//'):
		return 'https:' + image_url
	return image_url

#============================

def download_image(image_url: str, filename: str) -> str:
	"""
	Download an image from a URL and save it locally.
	"""
	if image_url is None:
		raise TypeError
	if os.path.exists(filename):
		return filename
	image_url = normalize_image_url(image_url)
	time.sleep(random.random())
	r = requests.get(image_url, stream=True)
	if r.status_code == 200:
		r.raw.decode_content = True
		with open(filename, 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print(f'.. image successfully downloaded: {filename}')
	else:
		print(f"!! image couldn't be retrieved: {image_url}")
		raise FileNotFoundError
	return filename

#============================

def process_image(raw_filename: str, processed_filename: str) -> str:
	"""
	Remove background and trim the image for label use.
	"""
	if os.path.exists(processed_filename):
		return processed_filename
	ensure_image_tools_installed()
	subprocess.run(['rembg', 'i', raw_filename, processed_filename], check=True)
	subprocess.run(['mogrify', '-trim', processed_filename], check=True)
	return processed_filename

#============================

def get_cached_image(image_url: str, image_prefix: str, item_id: str,
		raw_ext: str = 'jpg', processed_ext: str = 'png') -> str:
	"""
	Fetch, cache, and process an image, returning a path suitable for LaTeX.
	"""
	git_root = libbrick.path_utils.get_git_root()
	if git_root is None:
		images_dir = 'images'
	else:
		images_dir = os.path.join(git_root, 'images')
	ensure_images_directory(images_dir)
	raw_filename = os.path.join(images_dir, 'raw', f"{image_prefix}_{item_id}.{raw_ext}")
	processed_filename = os.path.join(
		images_dir, 'processed', f"{image_prefix}_{item_id}.{processed_ext}"
	)
	download_image(image_url, raw_filename)
	process_image(raw_filename, processed_filename)
	if git_root is None:
		return processed_filename
	return os.path.relpath(processed_filename, git_root)
