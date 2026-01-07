# URLs Package
# This package organizes URL patterns by domain for better maintainability
#
# Migration Note: During the transition phase, the original urls.py remains
# in place. New URL patterns should be added to the appropriate module file here.
# Once migration is complete, update the main project urls.py to include this package.

from django.urls import path, include

# URL patterns organized by domain
# TODO: Uncomment includes as modules are populated with URL patterns
urlpatterns = [
    # path('patients/', include('fred.urls.patient')),
    # path('doctors/', include('fred.urls.doctor')),
    # path('users/', include('fred.urls.user')),
    # path('offices/', include('fred.urls.office')),
    # path('rx/', include('fred.urls.rx')),
    # path('medications/', include('fred.urls.medication')),
    # path('orders/', include('fred.urls.order')),
    # path('shipments/', include('fred.urls.shipment')),
    # path('inventory/', include('fred.urls.inventory')),
    # path('lots/', include('fred.urls.lots')),
    # path('payments/', include('fred.urls.payment')),
    # path('communication/', include('fred.urls.communication')),
    # path('tasks/', include('fred.urls.task')),
    # path('logs/', include('fred.urls.logs')),
    # path('dashboard/', include('fred.urls.dashboard')),
    # path('customer-service/', include('fred.urls.customer_service')),
    # path('reference/', include('fred.urls.reference')),
    # path('eligibility/', include('fred.urls.eligibility')),
    # path('digital-health/', include('fred.urls.digital_health')),
    # path('vi/', include('fred.urls.vi')),
]
