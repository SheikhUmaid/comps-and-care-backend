# run_daphne.py
import os
from daphne.cli import CommandLineInterface

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

CommandLineInterface().run([
    "daphne",
    "-b", "0.0.0.0",
    "-p", "8000",
    "core.asgi:application"
])
