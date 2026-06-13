from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
def dashboard_page(request):
    
    if(request.session.get("id")):
        if("Prof" in request.session.get("permissions")):
            list_classes=python_functions.professor_get_classes(request)
            
        elif("Princ" in request.session.get("permissions") or "SUPER" in request.session.get("permissions")):
            list_classes=python_functions.principal_get_classes(request)
       
        context={
            'list_classes':list_classes,
         }
        return render(request,'dashboard.html',context)
    
    elif(request.session.get("RA")):
        ...
    else:
        messages.error(request,"Para acessar aquela página, é necessário se autenticar!")
        return redirect('matscholar_app:login_page')

def query_classname(request):
    if (request.session.get("id")):
        list_classes=python_functions.search_classes_by_classname(classname=request.POST.get("name_query"))