from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions

def std_cls_view_page(request):
    if(request.method=="POST" and request.session.get("RA")):
        try:
            class_query,assignments_query=python_functions.student_get_all_info_class(request)
            if class_query:
                context={
                    'class_query':class_query,
                    'assignments_query':assignments_query,
                }
                return render(request,'student/cls_view_page.html',context)
            else:
                return redirect("matscholar_app:dashboard_page")            
        except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    else:
        return redirect('matscholar_app:dashboard_page')
    
def std_assignment_view_page(request,assignment_id):
     if(request.session.get("RA") and request.session.get("actual_class_id")):
        try:
            assignment_query=python_functions.student_get_all_info_assignment(request,assignment_id)
            if assignment_query:
                context={
                    'assignment':assignment_query
                }
                return render(request,'student/assignment_view_page.html',context)
            else:
                return redirect("matscholar_app:std_cls_view_page")
        except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
     else:
         return redirect("matscholar_app:dashboard_page")