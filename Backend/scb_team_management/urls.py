from django.contrib import admin
from django.urls import path, include
from token_auth.urls import *
from users_management.urls import *
from admin_management.urls import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/samba/", include("users_management.urls")),
    path("security/", include("token_auth.urls")),
    path("admin-management/", include("admin_management.urls")),
]
