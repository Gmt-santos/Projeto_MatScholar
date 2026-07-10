from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
def prof_cls_edition_page(request):
    if(request.method== "POST" and "Prof" in request.session.get("permissions") and request.session.get("id")):
      
        try:
            if(request.session.get("actual_class_id")):
                valid_class_id=request.session.get("actual_class_id")
                again=True
            else:
             valid_class_id=python_functions.validate_ids_entries(request.POST.get("class"))
             again=False
            if valid_class_id:
                if again:
                    pass
                else:
                    valid_class_id=valid_class_id[0]
                
                listof_dict_assignments,class_query,qty_students=\
                python_functions.professor_cls_edition_get_all_info_classes(request,valid_class_id)
    
                
                if class_query and qty_students >=0 and request.session.get("actual_class_id"):
                    context={
                        "class_query":class_query,
                        "qty_students":qty_students,
                        "assignments_query":listof_dict_assignments
                    }
                    
                    return render(request,"professor/cls_edition_page.html",context=context)
                else:
                   
                    messages.error(request,"Erro ao consultar esse curso!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Dado inválido enviado no formulário!")
                return redirect("matscholar_app:dashboard_page")
                
        except (IndexError,TypeError,ValueError):
            messages.error(request,"Alteração indevida no formulário!")
            return redirect("matscholar_app:dashboard_page")
    else:
        return redirect("matscholar_app:dashboard_page")

def prof_assignment_view(request,assignment_id:None):
    if("Prof" in request.session.get("permissions") \
    and request.session.get("id") and assignment_id):
        try:
            is_valid_assignment_id=python_functions.validate_ids_entries(assignment_id)
            if(is_valid_assignment_id):
                validated_assignment_id=is_valid_assignment_id[0]
                assignment_query_dict,assignments_students_query_listof_dict=\
                python_functions.professor_get_all_info_assignment(request,validated_assignment_id)
                if assignment_query_dict:
                    context={
                        'assignment_info':assignment_query_dict,
                        'assignments_std_info':assignments_students_query_listof_dict,
                    }
                    return render(request,"professor/assignment_view_page.html",context=context)
            else:
                messages.error(request,"Dados inválidos enviados!")
                return redirect("matscholar_app:dashboard_page")
            
        except (IndexError,TypeError,ValueError):
            messages.error(request,"Alteração indevida no formulário!")
            return redirect("matscholar_app:dashboard_page")


    else:
        return redirect("matscholar_app:dashboard_page")

def prof_assignment_update_info(request):
    pass