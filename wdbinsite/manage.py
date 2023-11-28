#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Add project applications to Python Path
app_dir = '/Users/daher.37/Desktop/Research/APOGEE_Project/borja_WDs/wdbinsite/wdbinsite'
# app_dir = Path(__file__).resolve().parent / 'mswdbinsite/'
sys.path.insert(0, str(app_dir))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wdbinsite.main.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
