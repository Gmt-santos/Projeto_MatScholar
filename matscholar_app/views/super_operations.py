from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions

def super_princ_creation_page(request):
    try:
        if "SUPER" in request.session.get("permissions") and request.session.get("id"):
             safe_password=python_functions.generate_safe_password()
             context={
                  "safe_password":safe_password
             }
             return render(request,"super/princ_creation_page.html",context)
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:login_page")


def super_princ_creation_operation(request):
    try:
        if "SUPER" in request.session.get("permissions") and request.session.get("id") and request.method ==  "POST":
            valid_email=python_functions.regex_list_to_string(python_functions.email_validation(request.POST.get("email")))
            valid_password=python_functions.regex_list_to_string(
                 python_functions.validate_passwords_entries(request.POST.get("password")))
            valid_name=python_functions.regex_list_to_string(python_functions.validate_name_entries(request.POST.get("name")))
            valid_role=python_functions.regex_list_to_string(python_functions.validate_query_entries(request.POST.get("role")))
            if valid_email and valid_password and valid_name and valid_role:
                python_functions.super_add_principal(request,valid_name,valid_role,valid_password,valid_email)
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:login_page")


def super_prof_creation_page(request):
    try:
        if "SUPER" in request.session.get("permissions") and request.session.get("id"):
             safe_password=python_functions.generate_safe_password()
             context={
                  "safe_password":safe_password
             }
             return render(request,"super/prof_creation_page.html",context)
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:login_page")


def super_prof_creation_operation(request):
    try:
        if "SUPER" in request.session.get("permissions") and request.session.get("id") and request.method ==  "POST":
            valid_email=python_functions.regex_list_to_string(python_functions.email_validation(request.POST.get("email")))
            valid_password=python_functions.regex_list_to_string(
                 python_functions.validate_passwords_entries(request.POST.get("password")))
            valid_name=python_functions.regex_list_to_string(python_functions.validate_name_entries(request.POST.get("name")))
            valid_role=python_functions.regex_list_to_string(python_functions.validate_query_entries(request.POST.get("role")))
            if valid_email and valid_password and valid_name and valid_role:
                python_functions.super_add_professor(request,valid_name,valid_role,valid_password,valid_email)
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:login_page")
          