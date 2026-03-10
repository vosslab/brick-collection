"""Shared Textual TUI base class for task-runner scripts."""

import sys
import time
import asyncio
import argparse

try:
	# PIP3 modules
	from rich.text import Text
	from textual.app import App, ComposeResult
	from textual.containers import Horizontal, Vertical
	from textual.widgets import DataTable, RichLog, Static
	TEXTUAL_AVAILABLE = True
except ImportError:
	TEXTUAL_AVAILABLE = False


#============================================
def add_tui_args(parser: argparse.ArgumentParser) -> None:
	"""
	Add --tui/--cli mutually exclusive group to an argparse parser.

	Args:
		parser (argparse.ArgumentParser): The parser to add TUI flags to.
	"""
	tui_group = parser.add_mutually_exclusive_group()
	tui_group.add_argument(
		'-T', '--tui', dest='use_tui', action='store_true',
		help='use Textual TUI interface',
	)
	tui_group.add_argument(
		'-C', '--cli', dest='use_tui', action='store_false',
		help='use plain CLI output',
	)
	parser.set_defaults(use_tui=True)


#============================================
def should_use_tui(args: argparse.Namespace) -> bool:
	"""
	Decide whether to use the Textual TUI.

	Args:
		args (argparse.Namespace): Parsed arguments with use_tui attribute.

	Returns:
		bool: True if the TUI should be used.
	"""
	is_available = TEXTUAL_AVAILABLE and args.use_tui and sys.stdout.isatty()
	return is_available


if TEXTUAL_AVAILABLE:
	#============================================
	class TaskRunnerApp(App):
		"""
		Base Textual TUI app for running a list of tasks with progress tracking.

		Subclasses must implement:
			get_columns() -> list of (key, label) tuples
			get_row_label(task) -> str
			process_task(task) -> tuple of (ok: bool, summary: str)
		"""

		STATUS_STYLES = {
			"pending": "yellow",
			"running": "cyan",
			"ok": "green",
			"failed": "red",
		}

		CSS = (
			"#root { height: 1fr; }\n"
			"#top_row { height: 40%; min-height: 10; }\n"
			"#metrics_box { width: 30%; height: 1fr; border: solid gray; }\n"
			"#metrics_title { height: 1; }\n"
			"#metrics { height: 1fr; }\n"
			"#footer_note { height: 1; }\n"
			"#messages { width: 70%; height: 1fr; border: solid gray; }\n"
			"#task_table { height: 1fr; border: solid gray; }\n"
		)

		def __init__(self, tasks: list, title: str = "Task Runner") -> None:
			super().__init__()
			self.tasks = tasks
			self.app_title = title
			self.total = len(tasks)
			self.start_time = time.time()
			self.completed = 0
			self.durations = []
			self.log_lines = []
			self.task_rows = []
			self.column_keys = {}

		def format_status(self, status: str) -> Text:
			"""Format a status string with color styling."""
			style = self.STATUS_STYLES.get(status, "")
			if style:
				return Text(status, style=style)
			return Text(status)

		def get_columns(self) -> list:
			"""
			Return column definitions as a list of tuples.

			Each tuple is (key, label) or (key, label, width) where width
			is an optional integer to set a fixed column width.

			Must be implemented by subclasses.
			"""
			raise NotImplementedError

		def get_row_label(self, task) -> str:
			"""
			Return a display label for a task row.

			Must be implemented by subclasses.
			"""
			raise NotImplementedError

		def process_task(self, task) -> tuple:
			"""
			Process a single task. Runs in a background thread.

			Must be implemented by subclasses.

			IMPORTANT: Do NOT access Textual widgets from this method.
			Widget updates must be done through the returned column_updates dict.

			Returns:
				tuple: (ok: bool, summary: str, column_updates: dict)
				column_updates maps column key to display value, applied
				to the task table after the thread completes.
			"""
			raise NotImplementedError

		def compose(self) -> ComposeResult:
			"""Build the TUI layout."""
			with Vertical(id="root"):
				with Horizontal(id="top_row"):
					with Vertical(id="metrics_box"):
						yield Static(self.app_title, id="metrics_title")
						yield Static("Ready", id="metrics")
						yield Static("Press q to quit", id="footer_note")
					yield RichLog(id="messages", wrap=True, highlight=False)
				table = DataTable(id="task_table", zebra_stripes=True)
				table.cursor_type = "row"
				self.task_rows = []
				# Add the index column
				self.column_keys["index"] = table.add_column("#")
				# Add custom columns from subclass
				columns = self.get_columns()
				for col_def in columns:
					key = col_def[0]
					col_label = col_def[1]
					# Optional third element is column width
					col_width = col_def[2] if len(col_def) > 2 else None
					self.column_keys[key] = table.add_column(
						col_label, width=col_width
					)
				# Add the status column
				self.column_keys["status"] = table.add_column("status")
				self.column_keys["sec"] = table.add_column("sec")
				# Populate rows from tasks
				for idx, task in enumerate(self.tasks, start=1):
					label = self.get_row_label(task)
					# Truncate long labels
					if len(label) > 120:
						label = label[:117] + "..."
					# Build the row values: index, custom columns (empty), status, sec
					row_values = [str(idx)]
					row_values.extend([""] * len(columns))
					row_values.append(self.format_status("pending"))
					row_values.append("")
					row_key = table.add_row(*row_values)
					self.task_rows.append(row_key)
				yield table

		def on_mount(self) -> None:
			"""Start running tasks when the app is mounted."""
			self.run_worker(self.run_tasks, exclusive=True)

		def append_log(self, message: str) -> None:
			"""Append a message to the log panel with a 200-line cap."""
			self.log_lines.append(message)
			if len(self.log_lines) > 200:
				self.log_lines = self.log_lines[-200:]
			log_widget = self.query_one(RichLog)
			log_widget.write(message)

		def update_metrics(self) -> None:
			"""Update the metrics panel with progress, elapsed, and ETA."""
			elapsed = time.time() - self.start_time
			if self.completed > 0:
				avg = sum(self.durations) / self.completed
				eta = avg * (self.total - self.completed)
			else:
				eta = 0.0
			metrics = (
				f"Completed: {self.completed}/{self.total}\n"
				f"Elapsed: {elapsed:.1f}s\n"
				f"ETA: {eta:.1f}s"
			)
			self.query_one("#metrics", Static).update(metrics)

		def update_row_column(self, idx: int, column_key: str, value) -> None:
			"""Update a specific cell in the task table."""
			table = self.query_one(DataTable)
			row_key = self.task_rows[idx]
			table.update_cell(row_key, self.column_keys[column_key], value)

		async def run_tasks(self) -> None:
			"""Iterate through tasks, running each and updating the UI."""
			table = self.query_one(DataTable)
			for idx, task in enumerate(self.tasks):
				# Mark row as running and scroll table to current task
				self.update_row_column(idx, "status", self.format_status("running"))
				table.move_cursor(row=idx)
				start = time.time()
				# Run process_task in a background thread via asyncio
				ok, summary, column_updates = await asyncio.to_thread(
					self.process_task, task
				)
				duration = time.time() - start
				self.durations.append(duration)
				self.completed += 1
				# Apply column updates returned by process_task
				if column_updates:
					for col_key, col_value in column_updates.items():
						self.update_row_column(idx, col_key, col_value)
				# Update row status and time
				status = "ok" if ok else "failed"
				self.update_row_column(idx, "status", self.format_status(status))
				self.update_row_column(idx, "sec", f"{duration:.1f}")
				# Log the result
				label = self.get_row_label(task)
				if len(label) > 44:
					label = label[:41] + "..."
				self.append_log(f"{status.upper()} {label} ({duration:.1f}s)")
				if summary:
					self.append_log(summary[:2000])
				self.update_metrics()
			self.append_log("All tasks completed.")

		def on_key(self, event) -> None:
			"""Handle key presses."""
			if event.key == "q":
				self.exit()
