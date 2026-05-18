from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # LANDING PAGE
    path('', views.landing_page, name='landing'),

    # USER HOME PAGE
    path('home/', views.home, name='home'),

    # LOGIN
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),

    # LOGOUT
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # FEATURES
    path('yield/', views.yield_view, name='yield'),
    path('disease/', views.disease_view, name='disease'),
    path("dashboard",views.dashboard_view, name='dashboard'),

    # REGISTER
    path('register/', views.register_view, name='register'),
    path('', views.landing_page, name='landing_page')
]