from django.shortcuts import render,redirect
from django.contrib import messages
from utils import python as python_functions
def princ_std_creation_courses(request):
    if(request.session.get("id") and "Princ" in request.session.get("permissions")): 
        courses_query=python_functions.principal_std_creation_courses(request)
        if(courses_query):
        
            context={
                "courses_query":courses_query,
            }
            return render(request,"principal/std_creation_courses.html",context)
        else:
            return redirect("matscholar_app:dashboard_page")
    else:
        return redirect("matscholar_app:dashboard_page")
def princ_std_creation_forms(request):
    from matscholar_app.models import courses

    try:
        if(request.method=="POST" and request.session.get("id") and "Princ" in request.session.get("permissions")):
            course_id=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(request.POST.get("course")))
            if(course_id):
                if(courses.objects.filter(id=course_id,fk_institution=request.session.get("institution")).exists()):
                    recommended_password=python_functions.generate_safe_password()
                    valid_RA=python_functions.generate_RA(request=request)
                    context={
                        "course_id":course_id,
                        "recommended_password":recommended_password,
                        "actual_year":python_functions.get_year(),
                        'valid_RA':valid_RA,
                    }
                    return render(request,'principal/std_creation_forms.html',context=context)
                else:
                    messages.error(request,"O curso escolhido não existe em sua instituição!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"O curso escolhido não existe em sua instituição!")
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")

    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_std_creation_operation(request):
    try:
        if(request.method=="POST" and request.session.get("id") and "Princ" in request.session.get("permissions")):
            password=python_functions.regex_list_to_string(
                python_functions.validate_passwords_entries(request.POST.get("password")))

            name=python_functions.regex_list_to_string(
                python_functions.validate_name_entries(entry=request.POST.get("name")))

            is_valid_ra=python_functions.validate_RA(request=request,ra=request.POST.get("RA"))
            is_valid_course:bool=python_functions.validate_course(request=request,id=request.POST.get("course_id"))
            if(password and name and is_valid_ra and is_valid_course):

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
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
 



def princ_crs_creation_info(request):
    if(request.session.get("id")):
        return render(request,"principal/crs_creation_info.html")
    else:
        return redirect("matscholar_app:dashboard_page")
    
def princ_crs_creation_classes(request):
    try:
        if(request.method ==  "POST"):
            if(request.session.get("id") and "Princ" in request.session.get("permissions")):
                name=python_functions.regex_list_to_string(
                    python_functions.validate_query_entries(entry=request.POST.get("name")))
                
                acronym=python_functions.regex_list_to_string(
                python_functions.validate_acronym_entries(entry=request.POST.get("acronym")))

                e_mec=python_functions.regex_list_to_string(
                python_functions.validate_ids_entries(entry=request.POST.get("e_mec")))

                max_length=python_functions.regex_list_to_string(
                python_functions.validate_ids_entries(entry=request.POST.get("max_length")))

                quant_classes=python_functions.regex_list_to_string(
                python_functions.validate_ids_entries(entry=request.POST.get("quant_classes")))

                if(name and acronym and e_mec and python_functions.validate_strictpositive_numbers_entries(max_length) 
                and python_functions.validate_strictpositive_numbers_entries(quant_classes)):
                    quant_classes=int(quant_classes)
                    context={
                        "course_name":name,
                        "course_acronym":acronym,
                        "course_e_mec":e_mec,
                        "course_max_length":max_length,
                        "course_quant_classes":quant_classes,
                        "in_range":range(0,quant_classes)
                    }
                    return render(request,"principal/crs_creation_classes.html",context=context)
                else:
                    messages.error(request,"Dado inapropriado enviado!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            messages.error(request,"Erro na submissão de formulário!")
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_crs_creation_classes_operation(request):
    try:
        if(request.method == "POST" and request.session.get("id") and "Princ" in request.session.get("permissions")):
            name=python_functions.regex_list_to_string(
            python_functions.validate_query_entries(entry=request.POST.get("course_name")))

            acronym=python_functions.regex_list_to_string(
            python_functions.validate_acronym_entries(entry=request.POST.get("course_acronym")))

            e_mec=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(entry=request.POST.get("course_e_mec")))

            max_length=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(entry=request.POST.get("course_max_length")))

            quant_classes=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(entry=request.POST.get("course_quant_classes")))
  
            if(name and acronym and e_mec and python_functions.validate_strictpositive_numbers_entries(max_length) 
            and python_functions.validate_strictpositive_numbers_entries(quant_classes)):


                python_functions.principal_crs_creation_classes(request,name,acronym,e_mec,max_length)
                return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Algum dado inválido foi enviado !")
                return redirect("matscholar_app:dashboard_page")
        else:
            messages.error(request,"Algum dado inválido foi enviado !")
            return redirect("matscholar_app:dashboard_page")
        
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        messages.error(request,"Erro desconhecido!")
        return redirect("matscholar_app:dashboard_page")
    
        
def princ_cls_creation_courses(request):
    try:
        if(request.session.get("id") and "Princ" in request.session.get("permissions")): 
            courses_query=python_functions.principal_cls_creation_courses(request)
            if(courses_query):
                context={
                    "courses_query":courses_query,
                }
                return render(request,"principal/cls_creation_courses.html",context)
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    
def princ_cls_creation_abs_classes(request):
    try:
        if(request.method == "POST" and request.session.get("id") and "Princ" in request.session.get("permissions")):
            if(request.session.get("actual_course")):
                # Caso o usuário já tenha inserido alguma sala já anteriormente e quer inserir mais
                course_id=request.session.get("actual_course")
            else:
                course_id=request.POST.get("course")

            valid_course_id=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(entry=course_id))
            if (valid_course_id):
                classes_query=python_functions.principal_cls_creation_get_abs_classes(request,valid_course_id)
                if classes_query:
                    context={
                        "classes_query":classes_query,
                    }
                    return render(request,"principal/cls_creation_abs_classes.html",context=context)
                else:
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Algum dado inválido foi enviado !")
                return redirect("matscholar_app:dashboard_page")
            
        else:
            return redirect("matscholar_app:dashboard_page")
        
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
def princ_cls_creation_forms(request):
    try:    
       
        if(request.method=="POST" and request.session.get("id") and "Princ" in request.session.get("permissions") and
        request.session.get("actual_course")):
            valid_id=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(request.POST.get("class")))
            if valid_id:
    
                valid_class=python_functions.get_and_validate_class(request,valid_id)
                academic_users_query=python_functions.search_professors_by_institution(request)
                if valid_class and academic_users_query:
                    dict_valid_class={
                        "name":valid_class[0][0],
                        "initial":valid_class[0][1],
                    }
                    list_of_academic_users=python_functions.generate_academic_users_query_listofdict(academic_users_query)
                    context={
                        "valid_class":dict_valid_class,
                        "academic_users":list_of_academic_users,
                    }
                    return render(request,"principal/cls_creation_forms.html",context=context)
                else:
                    messages.error(request,"Houve algum erro na consulta dos professores ou das salas!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Algum dado inválido foi enviado!")
                return redirect("matscholar_app:dashboard_page")
        else:
            messages.error(request,"Acesso indevido!")
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_cls_creation_operation(request):
    # try:
        if(request.method=="POST" and request.session.get("id") and "Princ" in request.session.get("permissions") and
        request.session.get("actual_course")and request.session.get("actual_class")):
            
            valid_max_length=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(request.POST.get("max_length")))

            valid_academic_user_id_before_db=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(request.POST.get("academic_user")))

            valid_start_date=python_functions.validate_date(request.POST.get("start_date"))
            valid_end_date=python_functions.validate_date(request.POST.get("end_date"))

            if valid_max_length and valid_start_date and valid_end_date and valid_academic_user_id_before_db:


                if(python_functions.validate_academic_user(request,valid_academic_user_id_before_db)):

                    
                    class_name=request.session.get("actual_class")
                    class_initial=request.session.get("actual_class_initial")
                    valid_academic_user_id_after_db=valid_academic_user_id_before_db
                    abs_class_name=python_functions.principal_cls_creation_validate_class(request,class_name)
                    if abs_class_name and class_name and abs_class_name ==  class_name:
                        if(python_functions.principal_cls_creation_operation_create_class(request,valid_max_length,class_name,class_initial,
                        valid_academic_user_id_after_db,valid_start_date,valid_end_date)):
                            
                            messages.success(request,f"A aula {class_name} foi inserida com sucesso!")
                            return render(request,"principal/cls_creation_again.html")
                        else:
                            return redirect("matscholar_app:dashboard_page")
                    else:
                        messages.error(request,"Alteração indevida no formulário!")
                        return redirect("matscholar_app:dashboard_page")
                else:
                     messages.error(request,"Alteração indevida no formulário!")
                     return redirect("matscholar_app:dashboard_page")
                    
            else:
                messages.error(request,"Algum dado inválido foi enviado pelo formulário")
                return redirect("matscholar_app:dashboard_page")
            
        else:

            return redirect("matscholar_app:dashboard_page")
        
    # except Exception as e:
    #     python_functions.receive_exceptions_and_deal(request,type(e).__name__)
    #     return redirect("matscholar_app:dashboard_page")
    
'''
Reaproveitamento do código de cls_creation_courses
'''
def princ_cls_edition_courses(request):
    try:
        if(request.session.get("id") and "Princ" in request.session.get("permissions")): 
            courses_query=python_functions.principal_cls_creation_courses(request)
            if(courses_query):
                context={
                    "courses_query":courses_query,
                }
                return render(request,"principal/cls_edition_courses.html",context)
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
        
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    

def princ_cls_edition_classes(request):
    try:

        if(request.method == "POST" and request.session.get("id") and "Princ" in request.session.get("permissions")):
            course_id=request.POST.get("course")
            valid_course_id=python_functions.regex_list_to_string(
            python_functions.validate_ids_entries(entry=course_id))
            if (valid_course_id):
                classes_query=python_functions.principal_cls_edition_get_open_classes(request,valid_course_id)
                if classes_query:
                    context={
                        "classes_query":classes_query,
                    }
                    return render(request,"principal/cls_edition_classes.html",context=context)
                else:
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Algum dado inválido foi enviado !")
                return redirect("matscholar_app:dashboard_page")
            
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")

def princ_cls_edition_page(request):
    if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")):
      
        try:
            if(request.session.get("actual_class_id")):
                valid_class_id=request.session.get("actual_class_id")
                
            else:
             valid_class_id=python_functions.regex_list_to_string(
             python_functions.validate_ids_entries(request.POST.get("class")))
             
            if valid_class_id:
                
                class_query,qty_students=python_functions.principal_cls_edition_get_all_info_classes(request,valid_class_id)
                academic_users_query=python_functions.search_professors_by_institution(request)
                if academic_users_query:
                
                    academic_users_query_list_of_dict=python_functions.generate_academic_users_query_listofdict(academic_users_query)
                else:
                    return redirect("matscholar_app:dashboard_page")
                
                if class_query and qty_students >=0 and request.session.get("actual_class_id"):
                   
                    context={
                        "class_query":class_query,
                        "qty_students":qty_students,
                        "academic_users":academic_users_query_list_of_dict,
                    }
                    
                    return render(request,"principal/cls_edition_page.html",context=context)
                else:
                   
                    messages.error(request,"Erro ao consultar esse curso!")
                    return redirect("matscholar_app:dashboard_page")
            else:
                messages.error(request,"Dado inválido enviado no formulário!")
                return redirect("matscholar_app:dashboard_page")
                
        except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    else:
        return redirect("matscholar_app:dashboard_page")
    
    
def princ_cls_edition_deletion(request):
        if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
            and request.session.get("actual_class_id")):
            try:
                python_functions.principal_cls_edition_delete_class(request)
                return redirect("matscholar_app:dashboard_page")
                   
            except (IndexError,TypeError,ValueError):
                messages.error(request,"Alteração indevida no formulário!")
                return redirect("matscholar_app:dashboard_page")
            
def princ_cls_edition_remove_student_page(request):
    if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
        and request.session.get("actual_class_id")):
        try:
            students_query=python_functions.principal_cls_edition_get_all_students_by_class(request)
            if students_query:
                context={
                    "students":python_functions.generate_student_query_listofdict(students_query),
                    "deletion":True
                }
                return render(request,"principal/cls_edition_view_std.html",context=context)
            else:
                messages.error(request,"Houve algum erro ou esta sala ainda não possui alunos!")
                return redirect("matscholar_app:cls_edition_page")
            
        except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    else:
        return redirect('matscholar_app:dashboard_page')

def princ_cls_edition_remove_student_operation(request):
    try:
        if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
            and request.session.get("actual_class_id")):

            if(python_functions.principal_cls_edition_del_students(request)):
                messages.success(request,"Alunos excluídos com sucesso!")
                return render(request,"principal/cls_edition_again.html")
            
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    
def princ_cls_edition_add_student_page(request,actual_students:int,max_students:int):
    try:
        if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
            and request.session.get("actual_class_id")):

            if python_functions.validate_ids_entries(actual_students) and python_functions.validate_ids_entries(max_students):

                new_std_number:int=request.POST.get("new_std_number")

                if(python_functions.validate_ids_entries(new_std_number)):
                    
                    if(int(new_std_number)<=(int(max_students)-int(actual_students))):
                        
                        students_query=python_functions.search_students_by_course(request,request.session.get("actual_class_id"),True)
                        if len(students_query)<len(range(0,int(new_std_number))):

                            context={
                                "new_std_number":range(0,len(students_query)),
                                "students":students_query,
                            }

                        else:
                            context={
                                "new_std_number":range(0,int(new_std_number)),
                                "students":students_query,
                            }
                        return render(request,"principal/cls_edition_view_std_course.html",context=context)
                        
                    else:
                        messages.error(request,"A quantidade de alunos digitada excede o máximo!")
                        return redirect("matscholar_app:cls_edition_page")
                else:
                    messages.error(request,"A quantidade de alunos digitada é inválida!")
                    return redirect("matscholar_app:cls_edition_page")
            else:
                messages.error(request,"Dados inválidos enviados!")
                return redirect("matscholar_app:cls_edition_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")

def princ_cls_edition_add_student_operation(request):
    try:
        if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
            and request.session.get("actual_class_id")):
           
            if python_functions.principal_cls_edition_add_students(request):
                messages.success(request,"Alunos adicionados!")
                return render(request,"principal/cls_edition_again.html")
            else:
                
                return redirect("matscholar_app:cls_edition_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    
    
def princ_cls_edition_view_student(request):
    try:
        if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
            and request.session.get("actual_class_id")):
            students_query=python_functions.principal_cls_edition_get_all_students_by_class(request)
            if students_query:
                context={
                    "students":python_functions.generate_student_query_listofdict(students_query),
                    "deletion":False,
                }
                return render(request,"principal/cls_edition_view_std.html",context=context)
            else:
                messages.error(request,'Não foram encontrados alunos para essa sala!')
                return redirect("matscholar_app:cls_edition_page")
        else:
            return redirect("matscholar_app:dashboard_page")
          
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    
def princ_cls_edition_update_operation(request):
    try:
        if(request.method=="POST" and "Princ" in request.session.get("permissions") and request.session.get("id")
            and request.session.get("actual_class_id")):
            if(python_functions.principal_cls_edition_update_cls(request)):
                messages.success(request,"Aula atualizada com sucesso!")
                return render(request,"principal/cls_edition_again.html")
            else:
                return redirect("matscholar_app:cls_edition_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    





def princ_std_edition_courses(request):
    try:
        if(request.session.get("id") and "Princ" in request.session.get("permissions")): 

            courses_query=python_functions.principal_cls_creation_courses(request) # Função reutilizada,ignorar nome
            if(courses_query):
                context={
                    "courses_query":courses_query,
                }
                return render(request,"principal/std_edition_courses.html",context)
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_std_edition_students(request):
    try:
        if request.session.get("id") and "Princ" in request.session.get("permissions") and request.method == "POST":
            students_query=python_functions.search_students_by_course(request,actual_class_id=None,adding_to_cls=None)
            if students_query:
                context={
                    "students":students_query,
                }
                return render(request,"principal/std_edition_students.html",context)
            else:
                messages.error(request,"Não há estudantes no curso escolhido!")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")

def princ_std_edition_page(request):
    try:
        if request.session.get("id") and "Princ" in request.session.get("permissions") and request.method == "POST":
            student_query=python_functions.principal_std_edition_get_all_info_students(request)
            if student_query:
                request.session["actual_student_RA"]=student_query[0]
                student_query_dict={
                    "RA":student_query[0],
                    "name":student_query[1],
                    "year_of_entry":student_query[2],
                }
                context={
                    "student":student_query_dict,
                }
                return render(request,"principal/std_edition_page.html",context=context)
            else:
                messages.error(request,"Aluno não encontrado em sua instituição!")
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    
def princ_std_edition_operation(request):
    try:
        if request.session.get("id") and "Princ" in request.session.get("permissions") and request.method == "POST" and \
         request.session.get("actual_student_RA"):
            if(python_functions.principal_std_edition_operation(request)):
                messages.success(request,"Estudante atualizado com sucesso!")
               
        
            return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")
    

def princ_crs_edition_courses(request):
    try:
        if(request.session.get("id") and "Princ" in request.session.get("permissions")): 
            courses_query=python_functions.principal_cls_creation_courses(request)
            if(courses_query):
                context={
                    "courses_query":courses_query,
                }
                return render(request,"principal/crs_edition_courses.html",context)
            else:
                return redirect("matscholar_app:dashboard_page")
        else:
            return redirect("matscholar_app:dashboard_page")
        
    except Exception as e:
            python_functions.receive_exceptions_and_deal(request,type(e).__name__)
            return redirect("matscholar_app:dashboard_page")


def princ_crs_edition_abs_classes(request):
    try:
            if(request.session.get("id") and "Princ" in request.session.get("permissions")):
                if(request.session.get("actual_course")):
                    # Caso o usuário já tenha inserido alguma sala já anteriormente e quer inserir mais
                    course_id=request.session.get("actual_course")
                else:
                    course_id=request.POST.get("course")

                valid_course_id=python_functions.regex_list_to_string(
                python_functions.validate_ids_entries(entry=course_id))
                if (valid_course_id):
                    classes_query=python_functions.principal_cls_creation_get_abs_classes(request,valid_course_id)
                    if classes_query:
                        request.session["actual_course"]=valid_course_id
                        context={
                            "classes_query":classes_query,
                        }
                        return render(request,"principal/crs_edition_abs_classes.html",context=context)
                    else:
                        return redirect("matscholar_app:dashboard_page")
                else:
                    messages.error(request,"Algum dado inválido foi enviado !")
                    return redirect("matscholar_app:dashboard_page")
                
            else:
                return redirect("matscholar_app:dashboard_page")
            
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_crs_edition_grade_finalization_page(request):
    try:
        if request.method == "POST" and request.session.get("id") and request.session.get("actual_course"):
            open_classes_query=python_functions.get_all_open_classes_grade_finalization(request,course_id=request.session.get("actual_course"))
            if open_classes_query:
                context={
                    'open_classes':open_classes_query,
                }
                return render(request,'principal/crs_edition_grade_finalization.html',context)
            else:
                return redirect("matscholar_app:dashboard_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_crs_edition_grade_finalization_operation(request):
    try:
        if request.method == "POST" and request.session.get("id") and request.session.get("actual_course"):
            python_functions.finalize_grades(request)
            return redirect("matscholar_app:dashboard_page")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")
    
def princ_crs_edition_graduates_verification(request):
    try:
        if request.method == "POST" and request.session.get("id") and request.session.get("actual_course"):
            listof_graduates,listof_risk_of_expulsion=python_functions.principal_get_info_possible_graduates(request)
            if listof_graduates or listof_risk_of_expulsion:
                context={
                    'graduates':listof_graduates,
                    'risk_of_expulsion':listof_risk_of_expulsion,
                }
                return render(request,"principal/crs_edition_graduates_view.html",context)
            else:
                messages.error(request,"Não há alunos formandos ou que estão além do prazo máximo de formação!")
                return redirect("matscholar_app:crs_edition_abs_classes")
    except Exception as e:
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page")       
    
def princ_crs_edition_graduates_operation(request):
    try:
       
        if request.method == "POST" and request.session.get("id") and request.session.get("actual_course"):
           
            python_functions.principal_update_graduates(request)
            return redirect("matscholar_app:dashboard_page")
            
    except Exception as e: 
        python_functions.receive_exceptions_and_deal(request,type(e).__name__)
        return redirect("matscholar_app:dashboard_page") 