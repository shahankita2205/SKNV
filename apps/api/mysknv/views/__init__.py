# Views Package
# This package organizes views/viewsets by domain for better maintainability
#
# Migration Note: During the transition phase, the original views.py remains
# in place. New views should be added to the appropriate module file here,
# then imported and exported via this __init__.py

# TODO: Uncomment imports as modules are populated with views
from .views import *
from .office import *

__all__ = []
