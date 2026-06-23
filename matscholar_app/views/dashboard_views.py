from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
from django.core.exceptions import PermissionDenied
def dashboard_page(request):
    '''
    Serve para caso o usuário não esteja mais interagindo com a sala ou o curso
    '''
    if request.session.get("actual_class"):
        del request.session["actual_class"]
    if request.session.get("actual_class_initial"):
        del request.session["actual_class_initial"]
    if request.session.get("actual_course"):
        del request.session["actual_course"]
    if request.session.get("actual_class_id"):
        del request.session["actual_class_id"]
    if request.session.get("actual_student_RA"):
        del request.session["actual_student_RA"]
    if(request.session.get("id")):
        if("Prof" in request.session.get("permissions")):
            list_classes=python_functions.professor_get_classes(request)
            
        elif("Princ" in request.session.get("permissions") or "SUPER" in request.session.get("permissions")):
            list_classes=python_functions.principal_get_classes(request)
        else:
            return redirect("matscholar_app:login_page")
        
        context={
            'list_classes':list_classes,
            'query_active':False,
         }
        return render(request,'dashboard.html',context)
    
    elif(request.session.get("RA")):
        list_classes=python_functions.student_get_classes(request)
        context={
            'list_classes':list_classes,
            'query_active':False,

        }
        return render(request,'dashboard.html',context)
    else:
        messages.error(request,"Para acessar aquela página, é necessário se autenticar!")
        return redirect('matscholar_app:login_page')

def query_classname(request):
    try:
        if(request.method == "POST"):

            if (request.session.get("id")):
                name_query=python_functions.validate_query_entries(request.POST.get("name_query"))
                if(name_query):
                    list_classes=python_functions.academic_users_search_classes_by_classname(request=request,classname=name_query[0])
                    if(list_classes):
                        context={
                            'list_classes':list_classes,
                            'query_active':True,
                            'query_classname':name_query[0]
                        }
                        return render(request,'dashboard.html',context=context)
                    else:
                        return redirect("matscholar_app:dashboard_page")
                else:
                    messages.error(request,"Nome inválido!")
                    return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except PermissionDenied:
        messages.error(request,"Erro de submissão de formulário!")
        return redirect("matscholar_app:dashboard_page")


def query_professorname(request):
    try:
        if(request.method ==  "POST"):
            if(request.session.get("id")):
                name_query=python_functions.validate_name_entries(request.POST.get("name_query"))
                if(name_query):
                    list_classes=python_functions.academic_users_search_classes_by_professorname(request=request,professorname=name_query[0])
                    context={
                        'list_classes':list_classes,
                        'query_active':True,
                        'query_classname':name_query[0]
                    }
                    return render(request,'dashboard.html',context=context)
                else:
                    messages.error(request,"Nome inválido!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except PermissionDenied:
        messages.error(request,"Erro de submissão de formulário!")
        return redirect("matscholar_app:dashboard_page")

def student_query_classname(request):
    try:
        if(request.method ==  "POST"):
            if(request.session.get("RA")):
                name_query=python_functions.validate_query_entries(request.POST.get("name_query"))
                if(name_query):
                    list_classes=python_functions.students_search_classes_by_classname(request=request,classname=name_query[0])
                    context={
                        'list_classes':list_classes,
                        'query_active':True,
                        'query_classname':name_query[0]
                    }
                    return render(request,'dashboard.html',context=context)
                else:
                    messages.error(request,"Nome inválido!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except PermissionDenied:
        messages.error(request,"Erro de submissão de formulário!")
        return redirect("matscholar_app:dashboard_page")

