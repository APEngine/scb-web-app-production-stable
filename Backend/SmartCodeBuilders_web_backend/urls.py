from django.contrib import admin
from django.urls import path, include
from authentification.urls import *
from UserTasks.urls import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/samba/', include('UserTasks.urls')),
    path('security/', include('authentification.urls'))
]
