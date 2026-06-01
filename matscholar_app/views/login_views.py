from django.shortcuts import render,redirect
from django.contrib import messages
from argon2 import PasswordHasher 
from utils import python as python_functions
def login_page(request):
    
    return render(request,'login.html')

def login_operation(request):
    if(request.method == "POST"):
        a=PasswordHasher()
        password_POST=request.POST.get("password")
        email_POST=request.POST.get("email")
        if(python_functions.email_validation(email_POST)):

            academic_user=python_functions.search_academic_users_by_email(email=email_POST)

            if academic_user:
                
              
                if python_functions.verify_hashed(password_POST=password_POST,academic_user=academic_user):
                    
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