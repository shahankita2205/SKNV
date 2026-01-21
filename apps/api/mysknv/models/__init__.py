# Models Package
# This package organizes models by domain for better maintainability
#
# Migration Note: During the transition phase, the original models.py remains
# in place. New models should be added to the appropriate module file here,
# then imported and exported via this __init__.py

from .models import *
from .office import *

__all__ = []
