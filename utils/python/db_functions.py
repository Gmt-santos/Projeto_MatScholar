from . import functions as f
from psycopg2 import OperationalError,errors,DatabaseError

from django.db import models
from redis import exceptions as r_exceptions
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned
from django.core.cache import cache
'''
Funções em Python
Serão descritas antes de sua definição
'''
'''
Gera RAs e verifica se eles existem no banco de dados,caso não,retorna o RA
'''
def generate_RA(request)-> str:
    from matscholar_app.models import students
    import random
    flag=1
    list_chars_numbers=['1','2','3','4','5','6','7','8','9','0']
    existent_ra=students.objects.filter(fk_institution=request.session.get("institution")).values_list("RA",flat=True)
    set_existent_ra=set(existent_ra)
    year=str(f.get_year()%2000)
    ra=year
    while flag == 1:
        for i in range(0,9):
            ra+=random.choice(list_chars_numbers)
        if(ra in set_existent_ra):
            flag=1
            ra=year
        else:
            flag=0
    return ra
'''
Validar o RA enviado na criação de estudantes------> Redundante
'''
def validate_RA(request,ra:str)-> bool:
    from matscholar_app.models import students
    import re as regex

    try:
        year=str(f.get_year()%2000)
        regex_ra=regex.findall(r"^[0-9]{11}$",ra)
        if regex_ra:
            existent_ra=students.objects.filter(fk_institution=request.session.get("institution")).values_list("RA",flat=True)
            set_existent_ra=set(existent_ra)
            
            if regex_ra[0] in set_existent_ra:
                return False
            else:
               
                return True
        else:
            return False
        
    except ObjectDoesNotExist as e:
       
        return False
    except EmptyResultSet as e:
      
        return False
    except MultipleObjectsReturned as e:
        
        return False
  
'''
Valida o curso do estudante a ser criado --> redundante
'''
def validate_course(request,id:str) ->bool:
    from matscholar_app.models import courses
    try:
        is_valid=f.validate_ids_entries(id)
        if is_valid:
            courses_id=courses.objects.filter(fk_institution=request.session.get("institution")).values_list("id",flat=True)
            set_courses_id=set(courses_id)
            if int(id) in set_courses_id:
                return True
            else:
                return False
        else:
            return False
    except ObjectDoesNotExist as e:
       
        return False
    except EmptyResultSet as e:
      
        return False
    except MultipleObjectsReturned as e:
        
        return False
    except ValueError:
        
        return False
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
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
        messages.error(request,"Erro desconhecido!")
        return False
    finally:
        if cursor is not None:
            cursor.close() 
        if conn is not None:
            conn.close()

'''
Valida o academic_user_id enviado na criação de salas (redundante)
'''
def validate_academic_user(request,academic_user_id)->bool:
    from matscholar_app.models import academic_users
    try:
       is_valid=academic_users.objects.filter(fk_institution=request.session.get("institution"),id=academic_user_id).exists()
       return is_valid
    except ObjectDoesNotExist as e:
       
        return False
    except EmptyResultSet as e:
      
        return False
    except MultipleObjectsReturned as e:
        
        return False
    except ValueError:
        
        return False



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
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
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
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
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
        except Exception as e:
            from django.contrib import messages
            messages.error(request,"Houve um erro na consulta de suas aulas!")
            messages.error(request,f"Erro:{e}")
            return False
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
    except OperationalError as e:
       
        messages.error(request,"Houve um erro na consulta de suas aulas!")
        messages.error(request,f"Erro:{e}")
        return False
    except r_exceptions.ConnectionError as e:
   
        messages.error(request,"Houve um erro na conexão com o banco de dados!")
        messages.error(request,f"Erro:{e}")
        return False
    except r_exceptions.TimeoutError as e:
    
        messages.error(request,"Tempo de consulta expirado!")
        messages.error(request,f"Erro:{e}")
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
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
    DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation):
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
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

    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation):
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except :
        conn.rollback()
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
            messages.error(request,f"Erro:{e}")
            return False
        
        except r_exceptions.TimeoutError as e:
    
            messages.error(request,"Tempo de consulta expirado!")
            messages.error(request,f"Erro:{e}")
            return False
    else:
        return False
    
'''
Faz a exata mesma coisa da função acima, foi criada mais com a intenção de deixar o código mais flexível a mudanças futuras
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
            messages.error(request,f"Erro:{e}")
            return False
        
        except r_exceptions.TimeoutError as e:
    
            messages.error(request,"Tempo de consulta expirado!")
            messages.error(request,f"Erro:{e}")
            return False
        except Exception as e:
            messages.error(request,"Erro desconhecido!")
            messages.error(request,f"Erro:{e}")
            return False
    else:
        return False

'''
Cria o estudante,com suas aulas iniciais e aulas "faltantes"
Código relativamente complexo, será explicado passo a passo
'''
def principal_std_creation_operation(request,password:str,name:str,valid_ra:str,valid_course:str)->bool:
    conn,cursor=None,None #Inicializa as variaveis de conexao
    try:
        conn,cursor=f.connection_cursor() #conecta com o servidor
        hashed_password=f.generate_hash(password) #Faz o Hashing da senha já validada na def std_creation_operation
        if(hashed_password):

            cursor.execute('insert into students("RA",name,year_of_entry,fk_course,password,fk_institution)values(%s,%s,%s,%s,%s,%s)',
                        [valid_ra,name,f.get_year(),valid_course,hashed_password,request.session.get("institution")])
            #Cria o estudante com o RA,nome,curso e senha validados,além de ser vinculado à instituição do criador

            cursor.execute('select classes.id from classes join classes_courses on classes.id=classes_courses.id_class join ' \
            'courses on classes_courses.id_course=courses.id where classes.open=1 and courses.fk_institution=%s and courses.id=%s and'
            ' classes.initial=1 and abstract=0',
            [request.session.get("institution"),valid_course])
            classes_initial=cursor.fetchall()
            
            # Busca os Ids das aulas que estão abertas,são iniciais(initial=1),não são abstratas(abstract=0),que tenham o id do curso
            # selecionado(courses.id) e que sejam da instituição do criador(courses.fk_institution)



            insert_into_classes_actual_str="insert into students_classes_actual(id,id_class,id_student)values"
            #Inicializa uma string para o insert
            for tupla in classes_initial:
                if tupla == classes_initial[-1]:
                    insert_into_classes_actual_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra});"
                else: 
                    insert_into_classes_actual_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra}),"
            # Percorre a lista de tuplas retornada pela busca anterior de Ids das aulas e adiciona esses Ids na string
            # do insert
            '''
            Se o usuário tentar criar um estudante sem nenhuma aula com open = 1 e abstract = 0, levanta erro aqui!
            '''
            cursor.execute(insert_into_classes_actual_str)
          
            #Insere na tabela 'students_classes_actual" os relacionamentos dos estudantes com as suas aulas atuais e ativas

            cursor.execute('select classes.id from classes join classes_courses on classes.id=classes_courses.id_class join ' \
            'courses on classes_courses.id_course=courses.id where classes.open=0 and courses.fk_institution=%s and courses.id=%s'
            'and abstract=1',
            [request.session.get("institution"),valid_course])
            # Busca os Ids das aulas que são da instituição do criador(courses_fk_institution),são do curso selecionado(courses.id)
            # e que são abstratas. O que é ser abstrata?
            '''
            Ser abstrata é servir de base para a criação de outras salas,ou seja,ser genérica. Desse modo, pode-se analisar se o 
            estudante concluiu as X aulas necessárias para a conclusão do curso. Assim,quando o estudante ser aprovado em Y aula,
            a Y aula sumirá do student_classes_actual e sua equivalente abstrata também sumirá da student_classes_missing.
            
            '''
            
            classes_abstract=cursor.fetchall()
            insert_into_classes_missing_str="insert into students_classes_missing(id,id_class,id_student)values"
            for tupla in classes_abstract:
                if tupla == classes_abstract[-1]:
                    insert_into_classes_missing_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra});"
                else: 
                    insert_into_classes_missing_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra}),"
            
            cursor.execute(insert_into_classes_missing_str) #Fez a mesma operação já descrita acima
            conn.commit() # Faz o commit de todos os inserts --> Caso algo dê errado,dá rollback e anula os inserts
            return True # retorna verdadeiro caso o dê tudo certo
                
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        try:
            if conn:
             conn.rollback()
        except Exception:
             pass
        messages.error(request,"Erro desconhecido!")
    finally:
        if cursor is not None:
            cursor.close() 
        if conn is not None:
            conn.close()

'''
Cria as salas abstratas e as vinculam ao curso
Código relativamente complexo,será explicado ação por ação
'''
def principal_crs_creation_classes(request,name,acronym,e_mec,max_length)->bool:
    from psycopg2 import errors,errorcodes
    from psycopg2.extras import execute_values
    from django.contrib import messages
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor() #Inicializa a conexão
        if conn and cursor:
            # Insere (sem fzr commit) o curso anteriormente digitado pelo usuário (todas as variáveis foram previamente validadas)
            cursor.execute("insert into courses(name,acronym,e_mec,max_length,fk_institution)values(%s,%s,%s,%s,%s) returning id",
                           [name,acronym,e_mec,max_length,request.session.get("institution")])
            
            course_id:list=cursor.fetchone()[0] # Guarda o Id do novo curso (returning id)
            list_inputs_name:list=request.POST.getlist("class_id") # Pega os nomes digitados pelo usuário
            list_inputs_initial:list=request.POST.getlist("class_initial") # Pega as informações dos selects(inicial)
            list_values=[] #inicializa a lista de valores para o insert no banco
            
            for i in range(0,len(list_inputs_name)):
                if not f.validate_query_entries(list_inputs_name[i]): #Caso o usuário digite algo inválido,ele retorna falso 
                    # e cancela a operação
                    messages.error(request,"Dado inválido enviado no formulário!")
                    conn.rollback()
                    return False
                else:
                    
                    # list_values.append((nome,open,initial,abstract))
                    if list_inputs_initial[i] == "1":
                             list_values.append((list_inputs_name[i],0,1,1))
                    elif list_inputs_initial[i] == "0" :
                             list_values.append((list_inputs_name[i],0,0,1))
               
                    else:
                        #Caso o usuário digite algo inválido,ele retorna falso 
                        # e cancela a operação
                        messages.error(request,"Dado inválido enviado no formulário!")
                        conn.rollback()
                        return False
            # Retorna uma lista de tuplas
            classes_id:list=execute_values(cursor,"insert into classes(name,open,initial,abstract)values %s returning id",list_values,fetch=True)
            classes_id_size=len(classes_id) #Pega o tamanho dessa lista de tuplas
            #Inicializa uma string para o insert
            string_insert_into_classes_courses="insert into classes_courses(id,id_class,id_course)values"
            # Percorre toda a lista de tuplas,acrescentando os dados de classes_id na string acima
            for i in range(0,classes_id_size):
                if i == classes_id_size-1:
                    string_insert_into_classes_courses+=(f"({classes_id[i][0]}-{course_id},{classes_id[i][0]},{course_id});")
                else:
                    string_insert_into_classes_courses+=(f"('{classes_id[i][0]}-{course_id}',{classes_id[i][0]},{course_id}),")
            cursor.execute(string_insert_into_classes_courses)
            conn.commit() # Commita e faz a inserção definitiva
            messages.success(request,"Curso criado com sucesso! Crie as salas para prosseguir!")
            return True # Retorna True se tudo der certo
        
        # Caso dê errado, tratamos os erros tentando fazer o rollback das operações feitas anteriormente para evitar erros
        # e inconsistências no banco de dados
        
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close() 
        if conn is not None:
            conn.close()
       
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
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
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
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close() 
        if conn is not None:
            conn.close()
    
'''
Insere uma nova classe no banco de dados, também cria sua relação com o curso na tabela classes_courses
'''
def principal_cls_creation_operation_create_class(request,max_length,class_name,class_initial,academic_user_id,start_date,end_date):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if(conn and cursor):
            cursor.execute("insert into classes(name,max_students,start_date,end_date,open,fk_professor,initial,abstract)values" \
            "(%s,%s,%s,%s,%s,%s,%s,%s) returning id",
            [class_name,max_length,start_date,end_date,1,academic_user_id,class_initial,0])
            new_class_id=cursor.fetchone()[0]
            cursor.execute("insert into classes_courses(id,id_class,id_course)values(%s,%s,%s)",
                           [f"{new_class_id}-{request.session.get("actual_course")}",new_class_id,request.session.get("actual_course")])
            conn.commit()
            return True
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
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
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except errors.UndefinedColumn:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        try:
            conn.rollback()
        except Exception:
            pass
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception :
        if conn:
            try:
              conn.rollback()
            except Exception:
                pass
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    finally:
        if cursor is not None:
            cursor.close() 
        if conn is not None:
            conn.close()
