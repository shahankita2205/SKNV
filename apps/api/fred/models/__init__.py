# Models Package
# This package organizes models by domain for better maintainability
#
# Migration Note: During the transition phase, the original models.py remains
# in place. New models should be added to the appropriate module file here,
# then imported and exported via this __init__.py

# TODO: Uncomment imports as modules are populated with models
from .models import *
from .gen_ai_calling import *
from .logs import *
from .reference import *

from .doctor import Doctor
from .office import *

# from .patient import *
# from .user import *
# from .office import *
# from .rx import *
# from .medication import *
# from .order import *
# from .inventory import *
# from .payment import *
# from .communication import *
# from .task import *
# from .eligibility import *
# from .digital_health import *
# from .vi import *

__all__ = []
