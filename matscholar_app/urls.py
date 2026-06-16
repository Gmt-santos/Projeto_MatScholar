from django.contrib import admin
from django.urls import path,include
from . import views
app_name="matscholar_app"
urlpatterns = [
    path('',views.index,name="index"),
    path('login/',view=views.login_page,name="login_page"),
    path('login/login_operation_academic_user/',view=views.login_operation_academic_user,name='login_operation_academic_user'),
    path('login/login_operation_student/',view=views.login_operation_student,name='login_operation_student'),
    path('dashboard/',view=views.dashboard_page,name='dashboard_page'),
    path('dashboard/query_classname/',view=views.query_classname,name='query_classname'),
    path('dashboard/query_professorname/',view=views.query_professorname,name='query_professorname'),
    path('dashboard/principal/std_creation_courses/',view=views.std_creation_courses,name="std_creation_courses"),
    path('dashboard/principal/std_creation_forms/',view=views.std_creation_forms,name="std_creation_forms"),
    path('dashboard/principal/std_creation_operation/',view=views.std_creation_operation,name="std_creation_operation"),
    path('dashboard/principal/crs_creation_info/',view=views.crs_creation_info,name="crs_creation_info"),
    path('dashboard/principal/crs_creation_classes/',view=views.crs_creation_classes,name="crs_creation_classes"),
    path('logout/',view=views.logout,name="logout"),
]