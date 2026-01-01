# Standard Library
import os
import shutil
import subprocess

#============================
#============================
def compile_with_latexmk(tex_file: str, output_dir: str, pdf_file: str = None) -> None:
	"""
	Compile a LaTeX file with latexmk using xelatex.
	"""
	if tex_file is None:
		raise ValueError("tex_file is required")
	if output_dir is None:
		raise ValueError("output_dir is required")
	if shutil.which('latexmk') is None:
		raise FileNotFoundError("latexmk not found in PATH")
	command = _build_latexmk_command(tex_file, output_dir)
	result = _run_latexmk(command)
	if result[0] != 0:
		output = result[1]
		print(output)
		if 'gave an error in previous invocation of latexmk' in output:
			clean_command = _build_latexmk_clean_command(tex_file, output_dir)
			_run_latexmk(clean_command)
			result = _run_latexmk(command)
			if result[0] != 0:
				print(result[1])
				_report_latexmk_failure(tex_file, output_dir)
		else:
			_report_latexmk_failure(tex_file, output_dir)
	if pdf_file is not None:
		print(f'open "{pdf_file}"')

#============================
#============================
def _build_latexmk_command(tex_file: str, output_dir: str) -> list:
	command = [
		'latexmk',
		'-xelatex',
		'-interaction=nonstopmode',
		'-halt-on-error',
		'-file-line-error',
		f'-outdir={output_dir}',
		tex_file,
	]
	print(" ".join(command))
	return command

#============================
#============================
def _build_latexmk_clean_command(tex_file: str, output_dir: str) -> list:
	command = [
		'latexmk',
		'-C',
		f'-outdir={output_dir}',
		tex_file,
	]
	print(" ".join(command))
	return command

#============================
#============================
def _run_latexmk(command: list) -> tuple:
	result = subprocess.run(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True
	)
	return (result.returncode, result.stdout)

#============================
#============================
def _report_latexmk_failure(tex_file: str, output_dir: str) -> None:
	log_name = os.path.splitext(os.path.basename(tex_file))[0] + '.log'
	log_path = os.path.join(output_dir, log_name)
	print(f"Error: latexmk failed, see {log_path}")
	raise RuntimeError("latexmk failed")
