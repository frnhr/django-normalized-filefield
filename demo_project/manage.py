#!/usr/bin/env python
import os
import sys


# add parent directory to PYTHONPATH:
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
