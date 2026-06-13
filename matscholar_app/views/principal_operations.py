from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
def std_creation_courses(request):
    courses_query=python_functions.principal_std_creation_courses(request)
    if(courses_query):
        context={
            "courses_query":courses_query,
        }
        print(courses_query)
        return render(request,"std_creation_courses.html",context)
    else:
        return redirect("matscholar_app:dashboard_page")