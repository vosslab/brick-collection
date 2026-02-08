# Standard Library
import pathlib
import re

# PIP3 modules
import PIL.Image

# local repo modules
import libbrick.reportlab_label_utils
import reportlab_make_minifig_labels
import reportlab_make_set_labels


#============================================
def _write_sample_image(path: pathlib.Path) -> None:
	"""
	Create a simple sample image for rendering tests.
	"""
	image = PIL.Image.new("RGB", (80, 120), color=(220, 220, 220))
	image.save(path)


#============================================
def _count_pdf_pages(path: pathlib.Path) -> int:
	"""
	Count PDF pages by scanning page object markers.
	"""
	data = path.read_bytes()
	matches = re.findall(rb"/Type\s*/Page\b", data)
	return len(matches)


#============================================
def test_render_set_labels_smoke(tmp_path: pathlib.Path) -> None:
	"""
	Render a small set-label PDF and verify output exists.
	"""
	image_path = tmp_path / "sample_set.png"
	_write_sample_image(image_path)

	labels = []
	image_paths = []
	for index in range(11):
		labels.append(
			{
				"set_id": f"{1000 + index}-1",
				"lego_id": 1000 + index,
				"set_name": f"Set {index}",
				"name_size": 11.0,
				"category_name": "Theme",
				"year_released": "2020",
				"pieces_line": "100 pieces",
				"theme_name": "Theme",
				"year": "2020",
				"set_img_url": "https://example.com/x.jpg",
			}
		)
		image_paths.append(str(image_path))

	config = libbrick.reportlab_label_utils.with_debug_flags(
		libbrick.reportlab_label_utils.AVERY_5163_SET_CONFIG,
		True,
		True,
	)
	output_pdf = tmp_path / "set_labels.pdf"
	reportlab_make_set_labels.render_set_labels_pdf(labels, image_paths, str(output_pdf), config)
	assert output_pdf.exists()
	assert output_pdf.stat().st_size > 0
	assert _count_pdf_pages(output_pdf) == 3


#============================================
def test_render_minifig_labels_smoke(tmp_path: pathlib.Path) -> None:
	"""
	Render a small minifig-label PDF and verify output exists.
	"""
	image_path = tmp_path / "sample_minifig.png"
	_write_sample_image(image_path)

	labels = []
	image_paths = []
	for index in range(31):
		labels.append(
			{
				"minifig_id": f"fig{index}",
				"name": f"Name {index}",
				"name_size": 8.0,
				"year_released": "2021",
				"category_name": "Category",
				"superset_count": 2,
				"set_num": "1000",
			}
		)
		image_paths.append(str(image_path))

	config = libbrick.reportlab_label_utils.with_debug_flags(
		libbrick.reportlab_label_utils.AVERY_18260_MINIFIG_CONFIG,
		False,
		False,
	)
	output_pdf = tmp_path / "minifig_labels.pdf"
	reportlab_make_minifig_labels.render_minifig_labels_pdf(
		labels, image_paths, str(output_pdf), config
	)
	assert output_pdf.exists()
	assert output_pdf.stat().st_size > 0
	assert _count_pdf_pages(output_pdf) == 2
