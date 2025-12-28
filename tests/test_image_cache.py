import os

import libbrick.image_cache
import libbrick.path_utils

#============================
#============================
def test_normalize_image_url():
	"""
	Normalizes image URLs with missing schemes.
	"""
	assert libbrick.image_cache.normalize_image_url("//img.example.com/x.jpg") == "https://img.example.com/x.jpg"
	assert libbrick.image_cache.normalize_image_url("https://example.com/x.jpg") == "https://example.com/x.jpg"
	assert libbrick.image_cache.normalize_image_url(None) is None

#============================

def test_get_cached_image_paths(monkeypatch, tmp_path):
	"""
	Builds cached image paths and returns repo-relative processed path.
	"""
	def fake_download(image_url, filename):
		folder = os.path.dirname(filename)
		if not os.path.isdir(folder):
			os.makedirs(folder)
		with open(filename, "w") as f:
			f.write("x")
		return filename

	def fake_process(raw_filename, processed_filename):
		folder = os.path.dirname(processed_filename)
		if not os.path.isdir(folder):
			os.makedirs(folder)
		with open(processed_filename, "w") as f:
			f.write("y")
		return processed_filename

	monkeypatch.setattr(libbrick.path_utils, "get_git_root", lambda: str(tmp_path))
	monkeypatch.setattr(libbrick.image_cache, "download_image", fake_download)
	monkeypatch.setattr(libbrick.image_cache, "process_image", fake_process)
	result = libbrick.image_cache.get_cached_image("https://example.com/x.jpg", "set", "123")
	assert result == os.path.join("images", "processed", "set_123.png")
