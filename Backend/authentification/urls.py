from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path('login/', 
        views.HomeView.as_view(), 
        name ='login'),

    path('logout/', 
        views.LogoutView.as_view(), 
        name ='logout'),

    path('token/', 
        views.MyTokenObtainPairView.as_view(), 
        name ='token_obtain_pair'),

    path('token/refresh/', 
        jwt_views.TokenRefreshView.as_view(), 
        name ='token_refresh')
]