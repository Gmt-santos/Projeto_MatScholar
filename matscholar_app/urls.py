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
    path('logout/',view=views.logout,name="logout"),
    #       Dashboard       #       
    path('dashboard/',view=views.dashboard_page,name='dashboard_page'),
    path('dashboard/query_classname/',view=views.query_classname,name='query_classname'),
    path('dashboard/query_professorname/',view=views.query_professorname,name='query_professorname'),
    path('dashboard/std_query_classname/',view=views.student_query_classname,name="student_query_classname"),

    #       Principal urls      #
    
    #       Student_creation        #
    path('dashboard/principal/std_creation_courses/',view=views.princ_std_creation_courses,name="std_creation_courses"),
    path('dashboard/principal/std_creation_forms/',view=views.princ_std_creation_forms,name="std_creation_forms"),
    path('dashboard/principal/std_creation_operation/',view=views.princ_std_creation_operation,name="std_creation_operation"),
    #       Course_creation        #
    path('dashboard/principal/crs_creation_info/',view=views.princ_crs_creation_info,name="crs_creation_info"),
    path('dashboard/principal/crs_creation_classes/',view=views.princ_crs_creation_classes,name="crs_creation_classes"),
    path('dashboard/principal/crs_creation_classes_operation/',view=views.princ_crs_creation_classes_operation,name="crs_creation_classes_operation"),
    #       Class_creation         #
    path('dashboard/principal/cls_creation_courses/',view=views.princ_cls_creation_courses,name="cls_creation_courses"),
    path('dashboard/principal/cls_creation_abs_classes/',view=views.princ_cls_creation_abs_classes,name="cls_creation_abs_classes"),
    path('dashboard/principal/cls_creation_forms/',view=views.princ_cls_creation_forms,name="cls_creation_forms"),
    path('dashboard/principal/cls_creation_operation/',view=views.princ_cls_creation_operation,name="cls_creation_operation"),
    #       Class_edition      #
    path('dashboard/principal/cls_edition_courses/',view=views.princ_cls_edition_courses,name="cls_edition_courses"),
    path('dashboard/principal/cls_edition_classes/',view=views.princ_cls_edition_classes,name="cls_edition_classes"),
    path('dashboard/principal/cls_edition_page/',view=views.princ_cls_edition_page,name="cls_edition_page"),
    path('dashboard/principal/cls_edition_page/cls_update',view=views.princ_cls_edition_update_operation,name="cls_edition_update_operation"),
    path('dashboard/principal/cls_edition_page/cls_deletion',view=views.princ_cls_edition_deletion,name="cls_edition_deletion"),
    path('dashboard/principal/cls_edition_page/add_student_page/<str:actual_students>/<str:max_students>/',view=views.princ_cls_edition_add_student_page,name="cls_edition_add_student_page"),
    path('dashboard/principal/cls_edition_page/add_student_page/operation',view=views.princ_cls_edition_add_student_operation,name="cls_edition_add_student_operation"),
    path('dashboard/principal/cls_edition_page/remove_student_page',view=views.princ_cls_edition_remove_student_page,name="cls_edition_remove_student_page"),
    path('dashboard/principal/cls_edition_page/remove_student_page/operation',view=views.princ_cls_edition_remove_student_operation,name="cls_edition_remove_student_operation"),
    path('dashboard/principal/cls_edition_page/view_student/',view=views.princ_cls_edition_view_student,name="cls_edition_view_student"),
    #       Student_edition     #
    path('dashboard/principal/std_edition_courses/',view=views.princ_std_edition_courses,name='std_edition_courses'),
    path('dashboard/principal/std_edition_students/',view=views.princ_std_edition_students,name='std_edition_students'),
    path('dashboard/principal/std_edition_page/',view=views.princ_std_edition_page,name='std_edition_page'),
    path('dashboard/std_edition_page/operation/',view=views.princ_std_edition_operation,name='std_edition_operation'),
   
    #       Course_edition      #
    path('dashboard/principal/crs_edition_courses/',view=views.princ_crs_edition_courses,name='crs_edition_courses'),
    path('dashboard/principal/crs_edition_abs_classes/',view=views.princ_crs_edition_abs_classes,name='crs_edition_abs_classes'),
    path('dashboard/principal/crs_edition/grade_finalization/',view=views.princ_crs_edition_grade_finalization_page,name='crs_edition_grade_finalization_page'),
    path('dashboard/principal/crs_edition/grade_finalization/operation',view=views.princ_crs_edition_grade_finalization_operation,name='crs_edition_grade_finalization_operation'),
    #       Professor urls      #
    path('dashboard/professor/cls_edition_page/',view=views.prof_cls_edition_page,name='prof_cls_edition_page'),
    path('dashboard/professor/assignment_view/<str:assignment_id>/',view=views.prof_assignment_view,name='prof_assignment_view'),
    path('dashboard/professor/assignment_view/update_assignment_info/operation/',view=views.prof_assignment_update_info,name='prof_update_assignment_info'),
    path('dashboard/professor/assignment_view/update_assignment_std/operation/',view=views.prof_assignment_student_update,name='prof_update_assignment_std'),
    path('dashboard/professor/add_assignment_view/',view=views.prof_add_assignment_view,name="prof_add_assignment_view"),
    path('dashboard/professor/add_assignment_view/operation',view=views.prof_add_assignment,name='prof_add_assignment_operation'),
    path('dashboard/professor/del_assignment_view/',view=views.prof_del_assignment_view,name='prof_del_assignment_view'),
    path('dashboard/professor/del_assignment_view/operation/',view=views.prof_del_assignment_operation,name='prof_del_assignment_operation'),
    path('dashboard/professor/cls_edition_page/attendance/',view=views.prof_cls_edition_attendance,name='prof_attendance'),
    path('dashboard/professor/cls_edition_page/attendance/operation/',view=views.prof_cls_edition_attendance_operation,name='prof_attendance_operation'),
    
    #       Student urls        #
    path('dashboard/student/cls_view/',view=views.std_cls_view_page,name='std_cls_view_page'),
    path('dashboard/student/assignment_view/<str:assignment_id>/',view=views.std_assignment_view_page,name='std_assignment_view'),
    path('dashboard/student/final_grade_view/',view=views.std_view_final_grades_page,name='std_view_final_grades_page'),
]