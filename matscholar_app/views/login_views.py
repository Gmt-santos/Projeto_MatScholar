from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
def login_page(request):
    '''
    Serve para caso o usuário não esteja mais interagindo com a sala ou o curso
    '''
    if request.session.get('actual_assignment_id'):
        del request.session['actual_assignment_id']
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
    if(request.session.get("id") or request.session.get("RA")):
        return redirect("matscholar_app:dashboard_page")
    else:
        return render(request,'login.html')

def login_operation_academic_user(request):
    from django.core.exceptions import PermissionDenied
    from psycopg2 import OperationalError
    try:

            if(request.method == "POST"):

                password_POST=request.POST.get("password")
                email_POST=request.POST.get("email")
                if(python_functions.email_validation(email_POST) and python_functions.validate_passwords_entries(password_POST)):

                    academic_user=python_functions.search_academic_users_by_email(request,email=email_POST)
                    
                    if academic_user:
                        
                    
                        if python_functions.verify_hashed(password_POST=password_POST,password_db=academic_user["password"]):
                            python_functions.academic_users_set_session_attributes(request=request,dictionary=academic_user)
                            return redirect('matscholar_app:dashboard_page')
                        else:
                            messages.error(request,"Esse e-mail não está cadastrado ou a senha é incorreta!")
                            return render(request,"login.html")
                        
                    else:
                    
                        python_functions.hashing_false()
                        messages.error(request,"Esse e-mail não está cadastrado ou a senha é incorreta!")
                        return render(request,'login.html')
                else:
                    messages.error(request,"Esse e-mail não é válido ou a senha não é válida! ")
                    return render(request,'login.html')
            else:
                return redirect("matscholar_app:login_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:login_page")

def login_operation_student(request):
    try:
        if(request.method == "POST"):

            password_POST=request.POST.get("password")
            RA_POST=request.POST.get("RA")
            if(python_functions.validate_ids_entries(RA_POST)):

                student=python_functions.search_students_by_RA(request,RA_POST)

                if student:
                    
                    if python_functions.verify_hashed(password_POST=password_POST,password_db=student["password"]):
                            python_functions.students_set_session_attributes(request=request,dictionary=student)
                            return redirect("matscholar_app:dashboard_page")
                    else:
                        messages.error(request,"Esse RA não está cadastrado ou a senha é inválida")
                        return render(request,"login.html")
                    
                else:
                    
                    python_functions.hashing_false()
                    messages.error(request,"Esse RA não está cadastrado ou a senha é inválida")
                    return render(request,'login.html')
            else:
                messages.error(request,"Esse RA não é válido ")
                return render(request,'login.html')
        else:
            return redirect("matscholar_app:login_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:login_page")
    
def logout(request):
    from django.contrib.auth import logout
    try:
        logout(request)
        
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:login_page")