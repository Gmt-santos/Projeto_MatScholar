from django.shortcuts import render,redirect
from django.contrib import messages
def login_page(request):
    
    return render(request,'login.html')

def login_operation(request):
    if(request.method == "POST"):
        
        return redirect("matscholar_app:login_page")
    else:
        return redirect("matscholar_app:login_page")