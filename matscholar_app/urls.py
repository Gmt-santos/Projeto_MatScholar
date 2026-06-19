from django.contrib import admin
from django.urls import path,include
from . import views
app_name="matscholar_app"
urlpatterns = [
    #       Login       #
    path('',views.index,name="index"),
    path('login/',view=views.login_page,name="login_page"),
    path('login/login_operation_academic_user/',view=views.login_operation_academic_user,name='login_operation_academic_user'),
    path('login/login_operation_student/',view=views.login_operation_student,name='login_operation_student'),
    #       Dashboard       #       
    path('dashboard/',view=views.dashboard_page,name='dashboard_page'),
    path('dashboard/query_classname/',view=views.query_classname,name='query_classname'),
    path('dashboard/query_professorname/',view=views.query_professorname,name='query_professorname'),
    #       Student_creation        #
    path('dashboard/principal/std_creation_courses/',view=views.std_creation_courses,name="std_creation_courses"),
    path('dashboard/principal/std_creation_forms/',view=views.std_creation_forms,name="std_creation_forms"),
    path('dashboard/principal/std_creation_operation/',view=views.std_creation_operation,name="std_creation_operation"),
    #       Course_creation        #
    path('dashboard/principal/crs_creation_info/',view=views.crs_creation_info,name="crs_creation_info"),
    path('dashboard/principal/crs_creation_classes/',view=views.crs_creation_classes,name="crs_creation_classes"),
    path('dashboard/principal/crs_creation_classes_operation/',view=views.crs_creation_classes_operation,name="crs_creation_classes_operation"),
    #       Class_creation         #
    path('dashboard/principal/cls_creation_courses/',view=views.cls_creation_courses,name="cls_creation_courses"),
    path('dashboard/principal/cls_creation_abs_classes/',view=views.cls_creation_abs_classes,name="cls_creation_abs_classes"),
    path('dashboard/principal/cls_creation_forms/',view=views.cls_creation_forms,name="cls_creation_forms"),
    path('dashboard/principal/cls_creation_operation/',view=views.cls_creation_operation,name="cls_creation_operation"),
    #       Class_edition      #
    path('dashboard/principal/cls_edition_courses/',view=views.cls_edition_courses,name="cls_edition_courses"),
    path('dashboard/principal/cls_edition_classes/',view=views.cls_edition_classes,name="cls_edition_classes"),
    path('dashboard/principal/cls_edition_page/',view=views.cls_edition_page,name="cls_edition_page"),
    path('logout/',view=views.logout,name="logout"),
]