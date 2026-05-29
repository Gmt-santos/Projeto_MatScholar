from django.shortcuts import render,redirect
from django.contrib import messages
from argon2 import PasswordHasher
from utils import python as python_functions
def login_page(request):
    
    return render(request,'login.html')

def login_operation(request):
    if(request.method == "POST"):
        password_POST=request.POST.get("password")
        email_POST=request.POST.get("email")
        if(python_functions.email_validation(email_POST)):
            ...
        else:
            ...
        return redirect("matscholar_app:login_page")
    else:
        return redirect("matscholar_app:login_page")