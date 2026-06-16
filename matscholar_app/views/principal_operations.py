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
                    recommended_password=python_functions.generate_safe_password()
                    valid_RA=python_functions.generate_RA(request=request)
                    context={
                        "course_id":course_id,
                        "recommended_password":recommended_password,
                        "actual_year":python_functions.get_year(),
                        'valid_RA':valid_RA,
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
    except TypeError:
        messages.error(request,"Erro de submissão de formulário!")
        return redirect("matscholar_app:dashboard_page")
    
def std_creation_operation(request):
    try:
        if(request.method=="POST" and request.session.get("id")):
            password:list=python_functions.validate_passwords_entries(request.POST.get("password"))
            name:list=python_functions.validate_query_entries(entry=request.POST.get("name"))
            is_valid_ra:bool=python_functions.validate_RA(request=request,ra=request.POST.get("RA"))
            is_valid_course:bool=python_functions.validate_course(request=request,id=request.POST.get("course_id"))
            print(request.POST.get("course_id"))
            if(password and name and is_valid_ra and is_valid_course):

                password=password[0]
                name=name[0]
                valid_ra=request.POST.get("RA")
                valid_course=request.POST.get("course_id")
                if(python_functions.principal_std_creation_operation(request,password,name,valid_ra,valid_course)):
                    messages.success(request,"Aluno cadastrado com sucesso!")
                    messages.success(request,f"Aluno(a):{name}--RA:{valid_ra}--Senha(seja cuidadoso ao comunicar esse dado):{password}")
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Alguma informação enviada não é válida!")
                return redirect("matscholar_app:dashboard_page")
        else:

             return redirect("matscholar_app:dashboard_page")
    except TypeError:
        messages.error(request,"Erro de submissão de formulário!")
        return redirect("matscholar_app:dashboard_page")
    return redirect('matscholar_app:dashboard_page')



def crs_creation_info(request):
    if(request.session.get("id")):
        return render(request,"crs_creation_info.html")
    else:
        return redirect("matscholar_app:dashboard_page")
    
def crs_creation_classes(request):
    # try:
        if(request.method ==  "POST"):
            name:list=python_functions.validate_query_entries(entry=request.POST.get("name"))
            acronym:list=python_functions.validate_acronym_entries(entry=request.POST.get("acronym"))
            e_mec:list=python_functions.validate_ids_entries(entry=request.POST.get("e_mec"))
            max_length:list=python_functions.validate_ids_entries(entry=request.POST.get("max_length"))
            quant_classes:list=python_functions.validate_ids_entries(entry=request.POST.get("quant_classes"))
            if(name and acronym and e_mec and python_functions.validate_strictpositive_numbers_entries(max_length[0]) 
               and python_functions.validate_strictpositive_numbers_entries(quant_classes[0])):
                name=name[0]
                acronym=acronym[0]
                e_mec=e_mec[0]
                max_length=max_length[0]
                quant_classes=quant_classes[0]
                context={
                    "course_name":name,
                    "course_acronym":acronym,
                    "course_e_mec":e_mec,
                    "course_max_length":max_length,
                    "course_quant_classes":quant_classes,
                    "in_range":range(0,int(quant_classes))
                }
                return render(request,"crs_creation_classes.html",context=context)
            else:
                 messages.error(request,"Dado inapropriado enviado!")
                 return redirect("matscholar_app:dashboard_page")
        else:
            messages.error(request,"Erro na submissão de formulário!")
            return redirect("matscholar_app:dashboard_page")
    # except ValueError:
    #     messages.error(request,"Dado inapropriado enviado!")
    #     return redirect("matscholar_app:dashboard_page")
    # except TypeError:
    #     messages.error(request,"Erro na submissão de formulário!")
    #     return redirect("matscholar_app:dashboard_page")
