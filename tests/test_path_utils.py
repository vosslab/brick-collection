import subprocess

import libbrick.path_utils

#============================
#============================
def test_get_git_root_success(monkeypatch, tmp_path):
	"""
	Returns the git root when git command succeeds.
	"""
	def fake_check_output(cmd, cwd=None, universal_newlines=None):
		return str(tmp_path) + "\n"
	monkeypatch.setattr(
		libbrick.path_utils.subprocess,
		"check_output",
		fake_check_output,
	)
	result = libbrick.path_utils.get_git_root(str(tmp_path))
	assert result == str(tmp_path)

#============================

def test_get_git_root_failure(monkeypatch, tmp_path):
	"""
	Returns None when git command fails.
	"""
	def fake_check_output(cmd, cwd=None, universal_newlines=None):
		raise subprocess.CalledProcessError(1, cmd)
	monkeypatch.setattr(
		libbrick.path_utils.subprocess,
		"check_output",
		fake_check_output,
	)
	assert libbrick.path_utils.get_git_root(str(tmp_path)) is None
