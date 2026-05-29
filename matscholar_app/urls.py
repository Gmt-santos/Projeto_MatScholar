from django.contrib import admin
from django.urls import path,include
from . import views
app_name="matscholar_app"
urlpatterns = [
    path('',views.index,name="index"),
    path('login/',view=views.login_page,name="login_page"),
    path('login/login_operation/',view=views.login_operation,name='login_operation'),
]