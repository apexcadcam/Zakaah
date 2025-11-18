"""Install / uninstall helpers for Zakaah app."""

from __future__ import annotations

from pathlib import Path
import sys


def _ensure_app_in_apps_txt():
	"""Ensure zakaah is in apps.txt - called automatically during installation."""
	try:
		# Import and run setup_hook
		setup_hook_path = Path(__file__).parent.parent.parent / "setup_hook.py"
		if setup_hook_path.exists():
			import subprocess
			result = subprocess.run(
				[sys.executable, str(setup_hook_path)],
				capture_output=True,
				text=True,
				timeout=10
			)
			if result.returncode == 0 and result.stdout:
				print(result.stdout.strip())
	except Exception:
		# Silently fail - this is not critical for installation
		pass


def _remove_app_from_apps_txt():
	"""Remove zakaah from apps.txt - called automatically during uninstallation."""
	try:
		# Import and run setup_hook with remove argument
		setup_hook_path = Path(__file__).parent.parent.parent / "setup_hook.py"
		if setup_hook_path.exists():
			import subprocess
			result = subprocess.run(
				[sys.executable, str(setup_hook_path), "remove"],
				capture_output=True,
				text=True,
				timeout=10
			)
			if result.returncode == 0 and result.stdout:
				print(result.stdout.strip())
	except Exception:
		# Silently fail - this is not critical for uninstallation
		pass


def after_install() -> None:
	"""Called after app installation."""
	try:
		print("\n" + "=" * 70)
		print("📦 Installing Zakaah app...")
		print("=" * 70)
		
		# Ensure app is in apps.txt before installation
		_ensure_app_in_apps_txt()
		
		print("=" * 70)
		print("✅ Zakaah app installed successfully!")
		print("=" * 70 + "\n")
	except Exception as e:
		import frappe
		frappe.log_error(frappe.get_traceback(), "Zakaah Installation Error")
		print(f"\n❌ Error during installation: {str(e)}")
		print("   Check error logs for details.\n")
		# Don't re-raise to prevent installation failure


def before_uninstall() -> None:
	"""Called before app uninstallation."""
	try:
		print("\n" + "=" * 70)
		print("🗑️  Uninstalling Zakaah app...")
		print("=" * 70)
		
		# Remove app from apps.txt after successful uninstall
		_remove_app_from_apps_txt()
		
		print("=" * 70)
		print("✅ Zakaah app uninstalled successfully!")
		print("=" * 70 + "\n")
	except Exception:
		import frappe
		frappe.log_error(frappe.get_traceback(), "Zakaah Uninstall Error")
		print("\n❌ Error during uninstall. Check error logs for details.\n")

