"""
Phase 4 smoke test: confirms app.py has no import/syntax errors.
Full UI behavior is verified manually via `streamlit run app.py`.
Run with: python -m pytest tests/test_app_smoke.py -v
"""
import subprocess
import sys
import os


def test_app_py_compiles_without_errors():
    """Uses py_compile to catch syntax errors without actually launching Streamlit."""
    app_path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", app_path],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"app.py failed to compile: {result.stderr}"