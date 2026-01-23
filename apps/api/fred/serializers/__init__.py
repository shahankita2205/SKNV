# Serializers Package
# This package organizes serializers by domain for better maintainability
#
# Migration Note: During the transition phase, the original serializers.py remains
# in place. New serializers should be added to the appropriate module file here,
# then imported and exported via this __init__.py

# TODO: Uncomment imports as modules are populated with serializers
from .serializers import *
from .gen_ai_calling import *
from .logs import *
from .reference import *
from .dashboard import *
from .medication import *
from .patient import *
from .text import *

# Doctor serializers and service - fully migrated
from .doctor import *
from .office import *
from .address import *
from .payment import *
from .rx import *
from .rxfill import *
from .user import *
from .token import *
from .s3 import *
from .user import *

__all__ = []
