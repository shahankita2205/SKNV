# Views Package
# This package organizes views/viewsets by domain for better maintainability
#
# Migration Note: During the transition phase, the original views.py remains
# in place. New views should be added to the appropriate module file here,
# then imported and exported via this __init__.py

# TODO: Uncomment imports as modules are populated with views
from .views import *
from .gen_ai_calling import *
from .logs import *
from .reference import *
from .dashboard import *

# from .patient import *
# from .user import *
# from .office import *
# from .rx import *
# from .medication import *
# from .order import *
# from .shipment import *
# from .inventory import *
# from .lots import *
# from .payment import *
# from .communication import *
# from .task import *
# from .dashboard import *
# from .customer_service import *
# from .eligibility import *
# from .digital_health import *
# from .vi import *

# Doctor views - fully migrated
from .doctor import *
from .officetype import *

__all__ = []
