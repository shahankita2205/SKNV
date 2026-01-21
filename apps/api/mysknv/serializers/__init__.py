# Serializers Package
# This package organizes serializers by domain for better maintainability
#
# Migration Note: During the transition phase, the original serializers.py remains
# in place. New serializers should be added to the appropriate module file here,
# then imported and exported via this __init__.py

from .serializers import *
from .office import *

__all__ = []
