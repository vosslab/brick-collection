import subprocess
import sys
import re

def install(package):
	subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])

def is_installed(package):
	try:
		subprocess.check_call([sys.executable, "-m", "pip", "show", package])
		return True
	except subprocess.CalledProcessError:
		return False

with open('requirements.txt', 'r') as file:
	for line in file:
		package = line.strip()
		package = re.sub(r'\#.*$', '', package)
		if len(package) == 0:
			continue
		if not is_installed(package):
			print(f"\nInstalling {package}...")
			install(package)
		else:
			print(f"\n{package} is already installed.")
