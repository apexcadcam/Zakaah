"""Utility functions to check and start Frappe development server."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _get_bench_path() -> Path | None:
	"""Get the bench directory path."""
	try:
		import frappe
		# Try to get bench path from frappe
		bench_path = frappe.utils.get_bench_path()
		if bench_path:
			return Path(bench_path)
	except Exception:
		pass
	
	# Fallback: try to find bench path from current file location
	current_file = Path(__file__).resolve()
	# Go up from zakaah/zakaah/utils/server_check.py to bench root
	# apps/zakaah/zakaah/utils/server_check.py -> apps/zakaah -> apps -> bench
	for parent in current_file.parents:
		if (parent.parent / "sites").exists() and (parent.parent / "apps").exists():
			return parent.parent
	
	return None


def _is_server_running(port: int = 8000) -> bool:
	"""Check if the development server is running on the specified port."""
	try:
		# Try using ss command (modern Linux)
		result = subprocess.run(
			["ss", "-tlnp"],
			capture_output=True,
			text=True,
			timeout=2
		)
		if result.returncode == 0:
			return f":{port} " in result.stdout
	except Exception:
		pass
	
	try:
		# Fallback to netstat
		result = subprocess.run(
			["netstat", "-tlnp"],
			capture_output=True,
			text=True,
			timeout=2
		)
		if result.returncode == 0:
			return f":{port} " in result.stdout
	except Exception:
		pass
	
	# Last resort: check for process
	try:
		result = subprocess.run(
			["pgrep", "-f", f"bench.*serve.*{port}"],
			capture_output=True,
			timeout=2
		)
		return result.returncode == 0
	except Exception:
		return False


def _start_server(bench_path: Path, site_name: str | None = None, port: int = 8000) -> bool:
	"""Start the Frappe development server."""
	try:
		# Get site name from environment or use default
		if not site_name:
			# Try to get from sites directory
			sites_dir = bench_path / "sites"
			if sites_dir.exists():
				sites = [d for d in sites_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
				if sites:
					site_name = sites[0].name
		
		# Build command
		if site_name:
			cmd = ["bench", "--site", site_name, "serve", "--port", str(port)]
		else:
			cmd = ["bench", "serve", "--port", str(port)]
		
		# Start server in background
		log_file = bench_path / "logs" / "web.log"
		error_file = bench_path / "logs" / "web.error.log"
		
		with open(log_file, "a") as log, open(error_file, "a") as err:
			process = subprocess.Popen(
				cmd,
				cwd=str(bench_path),
				stdout=log,
				stderr=err,
				start_new_session=True
			)
		
		# Wait a moment to check if it started
		import time
		time.sleep(3)
		
		if _is_server_running(port):
			return True
		
		return False
	except Exception as e:
		print(f"Error starting server: {str(e)}")
		return False


def ensure_server_running(port: int = 8000, auto_start: bool = True) -> bool:
	"""
	Ensure the Frappe development server is running.
	
	Args:
		port: Port number to check (default: 8000)
		auto_start: If True, start server if not running
	
	Returns:
		True if server is running, False otherwise
	"""
	# Check if server is already running
	if _is_server_running(port):
		return True
	
	if not auto_start:
		return False
	
	# Get bench path
	bench_path = _get_bench_path()
	if not bench_path:
		print("⚠️  Could not determine bench path. Server check skipped.")
		return False
	
	# Try to start server
	print(f"🔄 Development server not running on port {port}. Attempting to start...")
	if _start_server(bench_path, port=port):
		print(f"✅ Development server started successfully on port {port}")
		print(f"   Access your site at: http://localhost:{port}")
		return True
	else:
		print(f"⚠️  Could not start development server automatically.")
		print(f"   Please start it manually with: bench serve --port {port}")
		return False

