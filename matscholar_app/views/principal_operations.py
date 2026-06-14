from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
def std_creation_courses(request):
    courses_query=python_functions.principal_std_creation_courses(request)
    if(courses_query):
        context={
            "courses_query":courses_query,
        }
        return render(request,"std_creation_courses.html",context)
    else:
        return redirect("matscholar_app:dashboard_page")
def std_creation_forms(request):
    from matscholar_app.models import courses
    from django.db.utils import OperationalError, DatabaseError,ProgrammingError
    from django.core.exceptions import PermissionDenied

    try:
        if(request.method=="POST" and request.session.get("id")):
            course_id=python_functions.validate_ids_entries(request.POST.get("course"))
            if(course_id):
                course_id=course_id[0]
                if(courses.objects.filter(id=course_id,fk_institution=request.session.get("institution")).exists()):
                    context={
                        "course_id":course_id,
                        
                    }
                    return render(request,'std_creation_forms.html',context=context)
                else:
                    messages.error(request,"O curso escolhido não existe em sua instituição!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"O curso escolhido não existe em sua instituição!")
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")

    except OperationalError:
        messages.error(request,"Houve algum erro com a conexão com o banco de dados!")
        return redirect("matscholar_app:dashboard_page")
    except DatabaseError:
        messages.error(request,"Houve algum erro com a conexão com o banco de dados!")
        return redirect("matscholar_app:dashboard_page")
    except ProgrammingError:
        messages.error(request,"Houve algum erro com a conexão com o banco de dados!")
        return redirect("matscholar_app:dashboard_page")
    except PermissionDenied:
        messages.error(request,"Erro de submissão de formulário!")
        return redirect("matscholar_app:dashboard_page")