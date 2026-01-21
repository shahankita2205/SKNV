"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from .views import get_status
from .views import (
    index,
    get_status as core_status,
    register,
    login,
    logout,
    me,
    stats,
    test,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from tasks.views import run_task

urlpatterns = [
    path("", index, name="index"),
    path("health/", core_status, name="health_check"),
    path("status/", core_status, name="get_status"),
    path("admin/", admin.site.urls),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("register/", register, name="register"),
    path("me/", me, name="me"),
    path("stats/", stats, name="stats"),
    path("test/", test, name="test"),
    path("api/fred/v1/", include("fred.urls")),
    path("api/mysknv/v1/", include("mysknv.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("tasks/<task_id>/", get_status, name="get_status"),
    path("tasks/", run_task, name="run_task"),
]
