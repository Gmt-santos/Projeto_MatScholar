from .. import functions as f
from .. import db_functions as dbf
from psycopg2 import OperationalError,errors,DatabaseError
from django.db import models
from redis import exceptions as r_exceptions
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned
from django.core.cache import cache



'''
Valida a sala abstrata do curso, a qual está sendo utilizada de base para a criação de uma sala não
abstrata , e retorna seus dados principais
'''
def get_and_validate_class(request,valid_id)->list[tuple]:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        cursor.execute("select classes.name,classes.initial from classes join classes_courses on classes.id=classes_courses.id_class join courses on " \
        "classes_courses.id_course=courses.id where courses.fk_institution=%s and classes.abstract=1 and classes.id=%s and courses.id=%s",
        [request.session.get("institution"),valid_id,request.session.get("actual_course")])
        valid_class=cursor.fetchall()
        request.session["actual_class"]=valid_class[0][0]
        request.session["actual_class_initial"]=valid_class[0][1]
        return valid_class

    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError,errors.UndefinedColumn):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
             
        messages.error(request,"Erro desconhecido!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



'''
Busca o objeto de usuario academico no banco de dados e devolve ele
'''
def search_academic_users_by_email(request,email:str)->dict:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            cursor.execute("select academic_users.id,academic_users.name,academic_users.role,academic_users.email,academic_users.password,academic_users.fk_institution,"
            "permissions.nickname from academic_users join academic_users_permissions on academic_users.id=academic_users_permissions.id_user join"
            " permissions on academic_users_permissions.id_nickname=permissions.id where academic_users.email like %s",[email,])
            academic_user=cursor.fetchall()

            if(academic_user):
                lista_permissoes=[]
                dictonary_user={
                    'id':None,
                    'name':None,
                    'role':None,
                    'email':None,
                    'password':None,
                    'fk_institution':None,
                    'permissions_nicknames':lista_permissoes,
                }
                for items in academic_user:
                    lista_permissoes.append(items[6])
                    dictonary_user={
                    'id':items[0],
                    'name':items[1],
                    'role':items[2],
                    'email':items[3],
                    'password':items[4],
                    'fk_institution':items[5],
                    'permissions_nicknames':lista_permissoes,
                }

                return dictonary_user
            else:
                return False
        else:
          messages.error(request,"Houve um erro com a conexão ao banco de dados!")
          return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Busca o objeto de estudante no banco de dados e devolve ele
'''
def search_students_by_RA(request,RA:str)->dict|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:

            cursor.execute('select "RA",name,year_of_entry,fk_course,password,fk_institution from students where "RA" like %s',(RA,))
            student=cursor.fetchone()
            if(student):
                dictonary_student={
                  'RA':student[0],
                  'name':student[1],
                  'year_of_entry':student[2],
                  'fk_course':student[3],
                  'password':student[4],
                  'fk_institution':student[5],
                }

                return dictonary_student
            else:
                return False
        else:
            raise EmptyResultSet
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
'''
Busca os estudantes pelo curso através do id da sala
Utilizado ao adicionar alunos nas salas
'''
def search_students_by_course(request,actual_class_id=None,adding_to_cls:bool=False)->list[dict]|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            if adding_to_cls:
                cursor.execute('select students."RA",students.name from students where students.fk_course = ' \
                'any(select courses.id from courses join classes_courses on courses.id=classes_courses.id_course where ' \
                'classes_courses.id_class = %s) and students."RA"!= all(select id_student from students_classes_actual ' \
                'where students_classes_actual.id_class=%s) and students.fk_institution=%s' \
                ,(actual_class_id,actual_class_id,request.session.get("institution")))
                
            else:
                cursor.execute('select students."RA",students.name from students where students.fk_course=%s and' \
                ' students.fk_institution=%s and students.graduated=0',
                               (request.POST.get("course"),request.session.get("institution")))
            students_query=cursor.fetchall()
            if students_query:
                students_query_listofdict=f.generate_student_query_listofdict(students_query)
                return students_query_listofdict
            else:
                messages.error(request,"Não há estudantes suficientes  no seu curso!")
                return False
        else:
            messages.error(request,"Houve um erro com a conexão do banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
       
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
'''
Busca os estudantes pela tarefa
Utilizada na assignment_view_page
"actual_assignment_id" já atribuída ao entrar nessa página
Já recebe conn e cursor inicializados
'''
def search_students_by_assignment(request,conn,cursor)->list[str]|bool:
    listof_RA=[]
    try:
       
        if conn and cursor:
            cursor.execute('select std."RA" from students as std join students_classes_actual as std_cls_act on' \
            ' std."RA" = std_cls_act.id_student join classes as cls on std_cls_act.id_class=cls.id join assignments as ass ' \
            'on cls.id = ass.fk_class where ass.id= %s and cls.fk_professor=%s and cls.id=%s and std.fk_institution=%s'
            ,[request.session.get("actual_assignment_id"),request.session.get("id"),request.session.get("actual_class_id"),
              request.session.get("institution")])
            
            for item in cursor.fetchall():
                listof_RA.append(item[0])

         
            return listof_RA
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
       
        return False
    
'''
 Busca as aulas que um determinado estudante tem no banco de dados
 Utilizado na entrada do dashboard_page
 '''
def student_get_classes(request)->list[dict]|bool:
    conn,cursor=None,None
    student_RA=request.session.get("RA")
    if(student_RA):
        try:
            conn,cursor=f.connection_cursor()
            if cache.get(f'student_RA_classes:{student_RA}'):
                list_classes_query_dicts=cache.get(f'student_RA_classes:{student_RA}')
                return list_classes_query_dicts
            else:
                if conn and cursor:
                    cursor.execute('select classes.id,classes.name,classes.start_date,classes.end_date,academic_users.name,' \
                    'academic_users.role,academic_users.email from academic_users join classes on academic_users.id=classes.fk_professor ' \
                    'join students_classes_actual on students_classes_actual.id_class=classes.id join students on students."RA" = ' \
                    'students_classes_actual.id_student where students."RA" like %s and classes.open=1',[student_RA,])
                    classes_query=cursor.fetchall()
                    list_classes_query_dicts:list[dict]=[]
                    for register in classes_query:
                        list_classes_query_dicts.append({
                            "class_id":register[0],
                            "class_name":register[1],
                            "start_date":register[2],
                            "end_date":register[3],
                            "academic_user_name":register[4],
                            "academic_user_role":register[5],
                            "academic_user_email":register[6],
                        })
                    cache.set(f'student_RA_classes:{student_RA}',list_classes_query_dicts,timeout=1200)
                    return list_classes_query_dicts
                else:
                    messages.error(request,"Houve um erro na conexão ao banco de dados!")
                    return False
        except(errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
                DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
             
            messages.error(request,"Algum dado inválido foi enviado!")
            return False
        except errors.UndefinedColumn:
             
            messages.error(request,"Algum dado inválido foi enviado!")
            return False
        except IndexError:
             
            messages.error(request,"Alteração no formulário detectada! Operação abortada!")
            return False
        except OperationalError:
             
            messages.error(request,"Houve um erro com a conexão do banco de dados!")
            return False
        except Exception :
            
         
            messages.error(request,"Algum dado inválido foi enviado!")
            return False
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
'''
 Busca as próximas tarefas que um determinado estudante tem no banco de dados
 Utilizado na entrada do dashboard_page
 '''
def student_get_assignments(request)->list[dict]:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            yesterday=f.date_to_string(f.get_today_date(deadline_comparison=True))
            cursor.execute("select ass.id,ass.name,ass.deadline,a_users.name,a_users.role,cls.name from assignments as ass" \
            " join classes as cls on ass.fk_class=cls.id join students_classes_actual as std_cls_actual on cls.id=" \
            "std_cls_actual.id_class join academic_users as a_users on cls.fk_professor=a_users.id where" \
            " std_cls_actual.id_student = %s and a_users.fk_institution = %s and ass.deadline>=%s " \
            "order by ass.deadline asc limit 5;",
            [request.session.get("RA"),request.session.get("institution"),yesterday])
            assignments_query=cursor.fetchall()
            if assignments_query:
                listof_assignments_dicts=[]
                for tupla in assignments_query:
                    listof_assignments_dicts.append({
                        'id':tupla[0],
                        'name':tupla[1],
                        'deadline':tupla[2],
                        'prof_name':tupla[3],
                        'prof_role':tupla[4],
                        'class_name':tupla[5], 
                    })
                return listof_assignments_dicts
            else:
                return False
        else:
            messages.error(request,"Houve um erro na conexão ao banco de dados!")
            return False
    except(errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
                DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
             
            messages.error(request,"Algum dado inválido foi enviado!")
            return False
    except errors.UndefinedColumn:
            
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
            
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
            
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()




'''
Puxa as salas que professor X dá aula e pode acessar e ver no dashboard
'''
def professor_get_classes(request)->dict | bool:
    from matscholar_app.models import classes

    professor_id=request.session.get("id")
    if(professor_id):
        try:
            if(cache.get(f"professor_id_classes:{professor_id}")):
                classes_query=cache.get(f"professor_id_classes:{professor_id}")

                return classes_query
            else:
                classes_query=classes.objects.filter(fk_professor=professor_id,open=1).values("id","name","start_date","end_date")
                if classes_query:
                    cache.set(f"professor_id_classes:{professor_id}",classes_query,timeout=1200)
                    return classes_query
                else:
                    return False
        except r_exceptions.ConnectionError as e:
            messages.error(request,"Houve um erro na conexão com o banco de dados!")
            return False

        except r_exceptions.TimeoutError as e:
            messages.error(request,"Tempo de consulta expirado!")
            return False
        
        except (ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned):
            messages.error(request,"Houve um erro na consulta ao banco de dados!")
            return False
        
        except Exception as e:
            messages.error(request,"Erro desconhecido!")
            return False
    else:
        return False

'''
Busca informações das aulas da instituição do diretor/coordenador da sessão
Disponibiliza no Dashboard e é usada logo após o login
'''
def principal_get_classes(request)->dict|bool:

    conn,cursor=None,None
    try:

        conn,cursor=f.connection_cursor()
        institution_id=request.session.get("institution")
        principal_id=request.session.get("id")
        if institution_id and principal_id:
            if(cache.get(f"institution_id_classes:{institution_id}")):
                classes_query=cache.get(f"institution_id_classes:{institution_id}")
                return classes_query

            else:
                cursor.execute(f"select classes.id,classes.name,classes.start_date,classes.end_date,academic_users.name,academic_users.email" \
                " from classes join academic_users on classes.fk_professor=academic_users.id where academic_users.fk_institution=%s and classes.open=1",
                [institution_id,])
                classes_query=cursor.fetchall()
                if classes_query:
                    lista=[]
                    for item in classes_query:
                        lista.append(
                            {
                                "id":item[0],
                                "name":item[1],
                                "start_date":item[2],
                                "end_date":item[3],
                                "professor_name":item[4],
                                "professor_email":item[5],
                            }
                        )

                    cache.set(f"institution_id_classes:{institution_id}",lista,timeout=1200)
                    return lista
                else:
                    return False

        else:
            messages.error(request,"A autenticação falhou!")
            return False
        
    except r_exceptions.ConnectionError as e:
        messages.error(request,"Houve um erro na conexão com o banco de dados!")    
        return False
    
    except r_exceptions.TimeoutError as e:
        messages.error(request,"Tempo de consulta expirado!")
        return False
    
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
    DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False

    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False

    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False

    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False


    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Procura aulas com o mesmo professor da sessão e de nome parecido com o digitado no campo de pesquisa
Usado no dashboard
'''
def academic_users_search_classes_by_classname(request,classname:str)->list[dict]|bool:
    academic_user_id=request.session.get("id")
    conn,cursor=None,None
    try:
        if(academic_user_id):
            permissions=request.session.get("permissions")
            if("Prof" in permissions):

                    conn,cursor=f.connection_cursor()
                    classname=f.string_to_querylike(string=classname)
                    cursor.execute("select classes.id,classes.name,classes.start_date,classes.end_date from classes join academic_users on " \
                    "classes.fk_professor=academic_users.id where academic_users.id=%s and classes.name like %s and classes.open=1"
                    ,[academic_user_id,classname])
                    classes_query=cursor.fetchall()
                    if(classes_query):
                        lista=[]
                        for item in classes_query:
                            lista.append(
                                {
                                    "id":item[0],
                                    "name":item[1],
                                    "start_date":item[2],
                                    "end_date":item[3],
                                }
                            )
                        return lista
                    return False


            elif("Princ" in permissions):
                    conn,cursor=f.connection_cursor()
                    classname=f.string_to_querylike(string=classname)
                    cursor.execute("select classes.id,classes.name,classes.start_date,classes.end_date,academic_users.name,academic_users.email" \
                    " from classes join academic_users on classes.fk_professor=academic_users.id where academic_users.fk_institution=%s" \
                    " and classes.open=1 and classes.name like %s",[request.session.get("institution"),classname])
                    classes_query=cursor.fetchall()
                    if(classes_query):
                        lista=[]
                        for item in classes_query:
                            lista.append(
                                {
                                    "id":item[0],
                                    "name":item[1],
                                    "start_date":item[2],
                                    "end_date":item[3],
                                    "professor_name":item[4],
                                    "professor_email":item[5],
                                }
                            )
                        return lista
                    else:
                        return False
            else:
                messages.error(request,"A autenticação falhou!")
                return False
        else:
            messages.error(request,"A autenticação falhou!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
    DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False

    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False

    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False

    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False


    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Busca aulas pelo nome do professor e pela instituição do diretor
'''
def academic_users_search_classes_by_professorname(request,professorname:str)->list[dict]|bool:

    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
                
            professorname=f.string_to_querylike(professorname)
            cursor.execute("select classes.id,classes.name,classes.start_date,classes.end_date,academic_users.name,academic_users.email from" \
            " classes join academic_users on classes.fk_professor=academic_users.id where academic_users.fk_institution =%s and" \
            " classes.open=1 and academic_users.name like %s ",[request.session["institution"],professorname])
            classes_query=cursor.fetchall()
            if(classes_query):
                        lista=[]
                        for item in classes_query:
                            lista.append(
                                {
                                    "id":item[0],
                                    "name":item[1],
                                    "start_date":item[2],
                                    "end_date":item[3],
                                    "professor_name":item[4],
                                    "professor_email":item[5],
                                }
                            )
                        return lista
            else:
                return False
        else:
            messages.error(request,"Houve um erro na conexão ao banco de dados!")
            return False

    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
        messages.error(request,"Algum dado inválido foi enviado!")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



'''
Quando o responsável com auth="Princ" quiser criar um aluno,essa função irá buscar os cursos disponíveis na instituição
'''

def principal_std_creation_courses(request)->models.QuerySet:

    from matscholar_app.models import courses
    
    institution_id=request.session.get("institution")
    if(request.session.get("id") and institution_id):
        try:
            courses_query=None
            if(cache.get(key=f'institution_courses={institution_id}')):
                courses_query=cache.get(key=f'institution_courses={institution_id}')

            else:
                courses_query=courses.objects.filter(fk_institution=institution_id).values("id",'name')
                cache.set(key=f'institution_courses={institution_id}',value=courses_query,timeout=1200)
            if not courses_query:
                messages.error(request,"Nenhum curso encontrado, entre em contato com a equipe de suporte!")
            return courses_query
        except r_exceptions.ConnectionError as e:

            messages.error(request,"Houve um erro na conexão com o banco de dados!")
           
            return False

        except r_exceptions.TimeoutError as e:

            messages.error(request,"Tempo de consulta expirado!")
         
            return False
        except (ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned):
            messages.error(request,"Houve um erro na consulta ao banco de dados!")
            return False
    else:
        return False

'''
Faz a exata mesma coisa da função acima, foi criada mais com a intenção de deixar o código mais flexível a mudanças futuras
Apesar do nome, foi reutilizada no std_edition_courses também
'''
def principal_cls_creation_courses(request)->models.QuerySet:
    from matscholar_app.models import courses
    institution_id=request.session.get("institution")
    if(request.session.get("id") and institution_id):
        try:
            courses_query=None
            if(cache.get(key=f'institution_courses={institution_id}')):
                courses_query=cache.get(key=f'institution_courses={institution_id}')

            else:
                courses_query=courses.objects.filter(fk_institution=institution_id).values("id",'name')
                cache.set(key=f'institution_courses={institution_id}',value=courses_query,timeout=1200)
            if not courses_query:
                messages.error(request,"Nenhum curso encontrado, entre em contato com a equipe de suporte!")
            return courses_query
        except r_exceptions.ConnectionError as e:

            messages.error(request,"Houve um erro na conexão com o banco de dados!")
        
            return False

        except r_exceptions.TimeoutError as e:

            messages.error(request,"Tempo de consulta expirado!")
           
            return False
        
        except (ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned):
            messages.error(request,"Houve um erro na consulta ao banco de dados!")
            return False
        
        except Exception as e:
            messages.error(request,"Erro desconhecido!")
          
            return False
        
    else:
        return False
    
'''
Busca as informações de salas abstratas no banco de dados ou no cache, a fim de usá-las na criação de salas "concretas"
'''
def principal_cls_creation_get_abs_classes(request,valid_course_id)->list[tuple]:
    conn,cursor=None,None
    try:
        if(cache.get(f"abs_classes:{valid_course_id}-{request.session.get("institution")}")):
                classes_query=cache.get(f"abs_classes:{valid_course_id}-{request.session.get("institution")}")
                request.session["actual_course"]=valid_course_id
                return classes_query
        else:
            conn,cursor=f.connection_cursor()
            if conn and cursor:
                cursor.execute("select classes.id,classes.name from classes join classes_courses on classes.id=classes_courses.id_class" \
                " join courses on classes_courses.id_course=courses.id where classes.abstract=1 and courses.id=%s and" \
                " courses.fk_institution = %s",[valid_course_id,request.session.get("institution"),])
                classes_query=cursor.fetchall()
                if(classes_query):
                    cache.set(key=f"abs_classes:{valid_course_id}-{request.session.get("institution")}",value=classes_query,timeout=1200)
                    request.session["actual_course"]=valid_course_id
                    return classes_query
                else:
                    messages.error(request,"Nenhum curso com esse código foi encontrado em sua instituição!")
                    return False
            else:
                messages.error(request,"Houve um erro com a conexão do banco de dados!")


    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
            
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def search_professors_by_institution(request)->list[tuple]|bool:
    conn,cursor=None,None
    try:
        if(cache.get(f"academic_users:{request.session.get("institution")}")):
            academic_users_query=cache.get(f"academic_users:{request.session.get("institution")}")
            return academic_users_query
        else:
            conn,cursor=f.connection_cursor()

            if( conn and cursor):
                cursor.execute("select academic_users.id,academic_users.name from academic_users join academic_users_permissions on" \
                " academic_users.id=academic_users_permissions.id_user where academic_users_permissions.id_nickname=3 and" \
                " academic_users.fk_institution = %s",[request.session.get("institution")])
                academic_users_query=cursor.fetchall()
                if(academic_users_query):
                    cache.set(f"academic_users:{request.session.get("institution")}",academic_users_query,timeout=1200)
                return academic_users_query
            else:
                messages.error(request,"Houve um erro com a conexão do banco de dados!")
                return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



'''
Reaproveitamendo da principal_cls_creation_get_abs_classes, só que buscando classes reais e abertas
'''
def principal_cls_edition_get_open_classes(request,valid_course_id)->list[tuple]:
    conn,cursor=None,None
    try:
        if(cache.get(f"open_classes:{valid_course_id}-{request.session.get("institution")}")):
                classes_query=cache.get(f"open_classes:{valid_course_id}-{request.session.get("institution")}")
                request.session["actual_course"]=valid_course_id
                return classes_query
        else:
            conn,cursor=f.connection_cursor()
            if conn and cursor:
                cursor.execute("select classes.id,classes.name from classes join classes_courses on classes.id=classes_courses.id_class" \
                " join courses on classes_courses.id_course=courses.id where classes.abstract=0 and open=1 and courses.id=%s and" \
                " courses.fk_institution = %s",[valid_course_id,request.session.get("institution"),])
                classes_query=cursor.fetchall()
                if(classes_query):
                    cache.set(key=f"open_classes:{valid_course_id}-{request.session.get("institution")}",value=classes_query,timeout=1200)
                    request.session["actual_course"]=valid_course_id
                    return classes_query
                else:
                    messages.error(request,"Nenhum curso com esse código foi encontrado em sua instituição!")
                    return False
            else:
                messages.error(request,"Houve um erro com a conexão do banco de dados!")


    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


'''
Utiliza o nome da sala digitada no campo de pesquisa pelo usuário do tipo student para procurar uma sala de aula aberta e não abstrata
, a qual o usuário está vinculado pela tabela student_classes_actual, além de procurar os dados do docente responsável por essa aula
'''

def students_search_classes_by_classname(request,classname)->list[dict]|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            class_name_query_like=f.string_to_querylike(classname)
            cursor.execute('select classes.id,classes.name,classes.start_date,classes.end_date,academic_users.name,' \
                'academic_users.role,academic_users.email from academic_users join classes on academic_users.id=classes.fk_professor ' \
                'join students_classes_actual on students_classes_actual.id_class=classes.id join students on students."RA" = ' \
                'students_classes_actual.id_student where students."RA" like %s and classes.open=1 and classes.name like %s',
                [request.session.get("RA"),class_name_query_like])
            classes_query=cursor.fetchall()

            list_classs_query_dicts:list[dict]=[]
            for register in classes_query:
                list_classs_query_dicts.append({
                    "class_id":register[0],
                    "class_name":register[1],
                    "start_date":register[2],
                    "end_date":register[3],
                    "academic_user_name":register[4],
                    "academic_user_role":register[5],
                    "academic_user_email":register[6],
                })
            return list_classs_query_dicts
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Recebe o id de uma sala e retorna quantos estudantes têm relacionamento com ela por meio da tabela studens_classes_actual
'''
def get_qty_students_by_class_id(conn,cursor,request,class_id)->int|bool:
    try:
        if conn and cursor:
            cursor.execute('select count(*) from students join students_classes_actual on'
            ' students."RA" = students_classes_actual.id_student where students_classes_actual.id_class=%s and'
            ' students.fk_institution=%s',[class_id,request.session.get("institution")])
            qty_students=cursor.fetchone()
            qty_students=qty_students[0]

            return qty_students
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False




'''
Adquire todos os dados de:id,nome,data de inicio,data de fim,numero maximo de estudantes,id do professor,nome do professor
e cargo do professor/profissional da sala escolhida na cls_edition_classes através do class_id(já validado)
Além disso,chama a função get_qty_students_by_class_id,passando a conexão,cursor e class_id. Sendo retornado o número de
alunos da sala que detém esse class_id.Retorna os dados mencionados na primeira linha e essa quantidade de alunos em uma
tupla
'''

def principal_cls_edition_get_all_info_classes(request,class_id)->tuple|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            cursor.execute('select classes.id,classes.name,classes.start_date,classes.end_date,classes.max_students,' \
            'academic_users.id,academic_users.name,academic_users.role from academic_users join classes on ' \
            'academic_users.id=classes.fk_professor where ' \
            'classes.id=%s and academic_users.fk_institution=%s and classes.open=1', \
            [class_id,request.session.get("institution")])
            class_query=cursor.fetchone()
            if class_query:
                request.session["actual_class_id"]=class_query[0]

                dict_class={
                    "class_name":class_query[1],
                    "class_start_date":f.date_to_string(class_query[2]),
                    "class_end_date":f.date_to_string(class_query[3]),
                    "class_max_students":class_query[4],
                    "academic_user_id":class_query[5],
                    "academic_user_name":class_query[6],
                    "academic_user_role":class_query[7],
                }

                qty_students=get_qty_students_by_class_id(conn,cursor,request,class_id)
                if qty_students>=0 and dict_class:
                    return dict_class,qty_students
                else:
                    return False,False
            else:
                messages.error(request,"O curso selecionado não existe na sua instituição de ensino!")
                return False,False
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False,False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False,False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False,False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



'''
Pega todos os estudantes de uma determinada sala e retorna uma lista de tuplas com seus RAs e nomes
Usada na exclusão dos relacionamentos entre estudante e sala
'''
def principal_cls_edition_get_all_students_by_class(request)->list[tuple]|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            cursor.execute('select students."RA",students.name from students join students_classes_actual on ' \
            'students."RA" = students_classes_actual.id_student where students_classes_actual.id_class = %s and ' \
            'students.fk_institution = %s',[request.session.get("actual_class_id"),request.session.get("institution")])
            students_query:list[tuple]=cursor.fetchall()
            return students_query
        else:
            messages.error(request,"Houve algum erro com a conexão ao banco de dados!")
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum erro na consulta ocorreu!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
        
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Pesquisa e retorna as informações de um estudante que está sendo editado
'''
def principal_std_edition_get_all_info_students(request)->list|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            valid_RA=f.validate_ids_entries(request.POST.get("student"))
            if valid_RA:
                valid_RA=valid_RA[0]
                cursor.execute('select "RA",name,year_of_entry from students where ' \
                'fk_institution=%s and "RA"=%s and graduated=0',(request.session.get("institution"),valid_RA))
                student_query=cursor.fetchone()

                return student_query
            else:
                messages.error(request,"Dado inválido enviado pelo formulário!")
                return False
        else:
           
            messages.error(request,"Erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
        
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



'''
Puxa as informações da sala,assim como suas tarefas. Assim, o professor pode acessar as tarefas e editá-las ou 
atribuir as notas
'''

def professor_cls_edition_get_all_info_classes(request,class_id)->tuple|bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            cursor.execute('select classes.id,classes.name,classes.start_date,classes.end_date from classes join academic_users on' \
            ' classes.fk_professor=academic_users.id where academic_users.fk_institution =%s and classes.id= %s and' \
            ' classes.open=1 and classes.fk_professor=%s',[request.session.get("institution"),class_id,
            request.session.get("id")])
            class_query=cursor.fetchone()
            if class_query:
                cursor.execute('select assignments.id,assignments.name,assignments.deadline ' \
                'from assignments where assignments.fk_class=%s'
                ,[class_id,])
                assignments_query=cursor.fetchall()
                listof_dict_assignments=[]
                if assignments_query:
                    for query in assignments_query:
        
                        listof_dict_assignments.append({
                            'id':query[0],
                            'name':query[1],
                            'deadline':query[2]
                        })
                
                request.session["actual_class_id"]=class_query[0]

                dict_class={
                    "class_name":class_query[1],
                    "class_start_date":class_query[2],
                    "class_end_date":class_query[3],
                }

                qty_students=get_qty_students_by_class_id(conn,cursor,request,class_id)
                if qty_students>=0 and dict_class:
                    return listof_dict_assignments,dict_class,qty_students
                else:
                    return False,False,False
            else:
                messages.error(request,"O curso selecionado não existe na sua instituição de ensino!")
                return False,False,False
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False,False,False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False,False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False,False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False,False,False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False,False,False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False,False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
'''
Após clicar no link para acessar a tarefa, essa função puxa todas as informações da tarefa e as informações das tarefas
dos alunos. Assim, o professor pode atualizar as tarefas dos alunos, assim como atualizar alguma informação da tarefa "mãe"
'''
def professor_get_all_info_assignment(request,assignment_id:str)->tuple:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if(conn and cursor):
            cursor.execute('select ass.id,ass.name,ass.desc,ass.deadline,ass.weight,ass.max_grade from assignments as ass where ass.fk_class=%s' \
            ' and ass.id = %s',[request.session.get("actual_class_id"),assignment_id])
            assignment_query:tuple=cursor.fetchone()
            if(assignment_query):
                assignment_query_dict={
                    'id':assignment_query[0],
                    'name':assignment_query[1],
                    'desc':assignment_query[2],
                    'deadline':f.date_to_string(assignment_query[3]),
                    'weight':assignment_query[4],
                    'max_grade':assignment_query[5],
                }
              
                cursor.execute('select std."RA",std.name,ass_std.grade,ass_std.feedback from ' \
                'assignments_students as ass_std' \
                ' join assignments as ass on ass_std.fk_assignment=ass.id join classes as cls on ass.fk_class=' \
                ' cls.id join students_classes_actual as std_cls_actual on cls.id=std_cls_actual.id_class join ' \
                ' students as std on std_cls_actual.id_student=std."RA"' \
                ' where cls.fk_professor=%s and cls.id=%s and ass.id= %s and std."RA" = ass_std.fk_student',
                [request.session.get("id"),
                request.session.get("actual_class_id"),assignment_id])
                assignments_students_query=cursor.fetchall()
               
                if(assignments_students_query):
                    assignments_students_query_listof_dict=f.generate_assignments_listof_dict(assignments_students_query)
                    return assignment_query_dict,assignments_students_query_listof_dict
                else:
                    messages.error(request,"Tarefa inválida acessada!")
                    return False,False
            else:
                messages.error(request,"Tarefa inválida acessada!")
                return False,False
            
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False,False


    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False,False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False,False
    except Exception :
         
             
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()




'''
Pega todos os estudantes de uma determinada sala e retorna uma lista de tuplas com seus RAs
Usada na criação do relacionamento de estudantes e tarefas
Sem finally,pois é usada dentro de outra função com a conexão aberta
'''
def professor_add_assignment_get_all_students_by_class(request,conn,cursor)->list[tuple]|bool:
    try:
    
        if conn and cursor:
            cursor.execute('select students."RA" from students join students_classes_actual on ' \
            'students."RA" = students_classes_actual.id_student where students_classes_actual.id_class = %s and ' \
            'students.fk_institution = %s',[request.session.get("actual_class_id"),request.session.get("institution")])
            students_query:list[tuple]=cursor.fetchall()
            return students_query
        else:
            messages.error(request,"Houve algum erro com a conexão ao banco de dados!")
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum erro na consulta ocorreu!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
        
        return False



'''
Pega todos os estudantes de uma determinada sala e retorna uma lista de tuplas com seus RAs e nomes
(Cópia da de cima,mas inicializando a conexão e puxando o nome)
'''
def professor_attendance_get_all_students_by_class(request,conn=None,cursor=None,already_connected=None)->list[tuple]|bool:
    if not(already_connected):
        conn,cursor=None,None
    try:
        if not(already_connected):
            conn,cursor=f.connection_cursor()
            
        if conn and cursor:
            cursor.execute('select students."RA",students.name from students join students_classes_actual on ' \
            'students."RA" = students_classes_actual.id_student join classes on students_classes_actual.id_class=classes.id' \
            ' where students_classes_actual.id_class = %s and ' \
            'students.fk_institution = %s and classes.fk_professor= %s'
            ,[request.session.get("actual_class_id"),request.session.get("institution"),request.session.get("id")])
            students_query:list[tuple]=cursor.fetchall()
            return students_query
        else:
            messages.error(request,"Houve algum erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum erro na consulta ocorreu!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
        
        return False
    finally:
        if already_connected is not True:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
'''
Pega todos os assignments de determinada sala.
Tudo já foi validado na student_get_all_info_class, então é garantido que esses assignments realmente pertencem ao usuário
solicitante
Sem finally,pois é chamada dentro da função student_get_all_info_class, a qual ainda usará a conexão
'''
def student_get_assignments_by_class(request,conn,cursor,class_id)-> list[dict]|bool:
    try:
        if conn and cursor:
            cursor.execute("select ass.id,ass.name,ass.deadline from assignments as ass where fk_class=%s",[class_id,])
            assignments_query:tuple[tuple]=cursor.fetchall()
            listof_assignments_dict=[]
            for assignment in assignments_query:
                listof_assignments_dict.append({
                    'id':assignment[0],
                    'name':assignment[1],
                    'deadline':assignment[2],
                })
            return listof_assignments_dict
        else:
            messages.error(request,"Houve algum erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
        messages.error(request,"Algum erro na consulta ocorreu!")
        return False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
        
        return False

'''
Puxa todas as informações das salas e combina elas com as informações da função acima e disponibiliza na 
página de visualização de sala para o estudante
'''
def student_get_all_info_class(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            if request.session.get("actual_class_id"):
                is_valid_class_id=f.validate_ids_entries(request.session.get("actual_class_id"))
            else:
                is_valid_class_id=f.validate_ids_entries(request.POST.get("id"))
            if is_valid_class_id:
                valid_class_id=is_valid_class_id[0]
                cursor.execute("select cls.name,cls.start_date,cls.end_date,a_users.name,a_users.role," \
                "std_cls_actual.attendance,std_cls_actual.absence from academic_users as a_users join classes as cls on" \
                " a_users.id=cls.fk_professor join students_classes_actual as std_cls_actual on" \
                " cls.id=std_cls_actual.id_class where cls.id=%s and std_cls_actual.id_student = %s and" \
                " a_users.fk_institution=%s",[valid_class_id,request.session.get("RA"),request.session.get("institution")])
                class_query:tuple=cursor.fetchone()
                if class_query:
                    class_dict={
                        'class_name':class_query[0],
                        'class_start_date':  class_query[1],
                        'class_end_date':  class_query[2],
                        'prof_name':  class_query[3],
                        'prof_role':  class_query[4],
                        'class_attendance':  class_query[5],
                        'class_absence': class_query[6],
                        'class_attendance_rate':f.get_attendance_rate
                        (attendance=class_query[5],absence=class_query[6],return_string=True)
                    }
                    assignments_query:list[dict]|bool=student_get_assignments_by_class(request,conn,cursor,valid_class_id)
                    request.session["actual_class_id"]=valid_class_id
                    return class_dict,assignments_query
                else:
                    messages.error(request,"A sala procurada não existe na sua instituição!")
                    return False,False
            else:
                messages.error(request,"Dado inválido enviado!")
                return False,False
        else:
            messages.error(request,"Houve algum erro com a conexão ao banco de dados!")
            return False,False
        
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
        DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        
        messages.error(request,"Algum erro na consulta ocorreu!")
        return False,False
    except errors.UndefinedColumn:
         
        messages.error(request,"Algum dado inválido foi enviado!")
        return False,False
    except IndexError:
         
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False,False
    except OperationalError:
         
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False,False
    except Exception as e :
         
             
        messages.error(request,"Erro desconhecido!")
        
        return False,False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Busca as informações da tarefa acessada na cls_view_page pelo id da tarefa.
Esse id vem via GET da url
'''
def student_get_all_info_assignment(request,assignment_id)->dict|bool:
        conn,cursor=None,None
    # try:
        is_valid_assignment_id=f.validate_ids_entries(assignment_id)
        if is_valid_assignment_id:
            valid_assignment_id=is_valid_assignment_id[0]
            conn,cursor=f.connection_cursor()
            if conn and cursor:
               
                cursor.execute("select ass.name,ass.desc,ass.weight,ass.max_grade,ass.deadline," \
                " ass_std.grade,ass_std.feedback from assignments_students as ass_std join assignments as ass on" \
                " ass_std.fk_assignment=ass.id join classes as cls on ass.fk_class=cls.id " \
                " where ass.id=%s and cls.id=%s and ass_std.fk_student=%s and ass.fk_class=%s and ass_std.fk_assignment=%s",
                [valid_assignment_id,request.session.get("actual_class_id"),
                 request.session.get("RA"),request.session.get("actual_class_id"),valid_assignment_id])
                
                assignment_query=cursor.fetchone()
                if assignment_query:
                    assignment_dict={
                        'ass_name':assignment_query[0],
                        'ass_desc': assignment_query[1],
                        'ass_weight':  assignment_query[2],
                        'ass_max_grade':  assignment_query[3],
                        'ass_deadline':assignment_query[4],
                        'std_grade':  assignment_query[5],
                        'prof_feedback':  assignment_query[6],
                    }
                    return assignment_dict
                else:
                    messages.error(request,'Tarefa inválida consultada!')
                    return False
            else:
                messages.error(request,"Houve algum erro com a conexão ao banco de dados!")
                return False
        else:
            messages.error(request,'Tarefa inválida consultada!')
            return False
    # except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
    #         DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
         
    #     messages.error(request,"Algum erro na consulta ocorreu!")
    #     return False
    # except errors.UndefinedColumn:
         
    #     messages.error(request,"Algum dado inválido foi enviado!")
    #     return False
    # except IndexError:
         
    #     messages.error(request,"Alteração no formulário detectada! Operação abortada!")
    #     return False
    # except OperationalError:
         
    #     messages.error(request,"Houve um erro com a conexão do banco de dados!")
    #     return False
    # except Exception as e :
         
             
    #     messages.error(request,"Erro desconhecido!")
        
    #     return False
    # finally:
    #     if cursor is not None:
    #         cursor.close()
    #     if conn is not None:
    #         conn.close()
