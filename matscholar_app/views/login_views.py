from django.shortcuts import render,redirect
from django.contrib import messages
from argon2 import PasswordHasher 
from utils import python as python_functions
def login_page(request):
    
    return render(request,'login.html')

def login_operation_academic_user(request):
    from django.core.exceptions import PermissionDenied
    from psycopg2 import OperationalError
    try:
        if(request.method == "POST"):
            
            password_POST=request.POST.get("password")
            email_POST=request.POST.get("email")
            if(python_functions.email_validation(email_POST) and python_functions.validate_passwords_entries(password_POST)):

                academic_user=python_functions.search_academic_users_by_email(email=email_POST)
                
                if academic_user:
                    
                
                    if python_functions.verify_hashed(password_POST=password_POST,academic_user=academic_user):
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
    except PermissionDenied:
        messages.error(request,"Erro na submissão do formulário!")
        return redirect("matscholar_app:login_page")
    except TypeError:
        messages.error(request,"Erro na submissão do formulário!")
        return redirect("matscholar_app:login_page")
    except OperationalError:
        messages.error(request,"Houve um erro na conexão com o banco de dados!")
        return redirect("matscholar_app:login_page")

def login_operation_student(request):
    # TODO
    if(request.method == "POST"):

        password_POST=request.POST.get("password")
        email_POST=request.POST.get("email")
        if(python_functions.email_validation(email_POST)):

            academic_user=python_functions.search_students_by_email(email=email_POST)
            
            if academic_user:
                
                
                if python_functions.verify_hashed(password_POST=password_POST,academic_user=academic_user):
                        python_functions.students_set_session_attributes(request=request,dictionary=academic_user)
                        return render(request,"login.html")
                else:
                    messages.error(request,"Esse e-mail não está cadastrado ou a senha é inválida")
                    return render(request,"login.html")
                
            else:
                
                python_functions.hashing_false()
                messages.error(request,"Esse e-mail não está cadastrado ou a senha é inválida")
                return render(request,'login.html')
        else:
            messages.error(request,"Esse e-mail não é válido ")
            return render(request,'login.html')
    else:
        return redirect("matscholar_app:login_page")
    
def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("matscholar_app:login_page")