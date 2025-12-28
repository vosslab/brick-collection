# Standard Library
import os
import subprocess

#============================
#============================
def get_git_root(path: str = None) -> str:
	"""
	Return the absolute path of the repository root.
	"""
	if path is None:
		path = os.path.dirname(os.path.abspath(__file__))
	try:
		base = subprocess.check_output(
			['git', 'rev-parse', '--show-toplevel'],
			cwd=path,
			universal_newlines=True
		).strip()
		return base
	except subprocess.CalledProcessError:
		# Not inside a git repository
		return None
