import os

import libbrick.msrp_loader
import libbrick.path_utils

#============================
#============================
def test_load_msrp_cache_from_repo(monkeypatch, tmp_path):
	"""
	Loads msrp cache from the repo CACHE directory.
	"""
	cache_dir = os.path.join(str(tmp_path), "CACHE")
	os.mkdir(cache_dir)
	cache_file = os.path.join(cache_dir, "msrp_cache.yml")
	with open(cache_file, "w") as f:
		f.write("123-1: 4999\n")
	monkeypatch.setattr(libbrick.path_utils, "get_git_root", lambda: str(tmp_path))
	data = libbrick.msrp_loader.load_msrp_cache()
	assert data["123-1"] == 4999

#============================

def test_load_msrp_cache_missing(monkeypatch, tmp_path):
	"""
	Returns empty dict when msrp cache is missing.
	"""
	monkeypatch.setattr(libbrick.path_utils, "get_git_root", lambda: str(tmp_path))
	data = libbrick.msrp_loader.load_msrp_cache()
	assert data == {}
