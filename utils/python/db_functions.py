from . import functions as f
from psycopg2 import OperationalError,errors


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
def generate_RA(request):
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
def validate_RA(request,ra:str):
    from matscholar_app.models import students
    import re as regex

    try:
        year=str(f.get_year()%2000)
        regex_ra=regex.findall(r"^[0-9]+$",ra)
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
def validate_course(request,id:str):
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
Busca o objeto de usuario academico no banco de dados e devolve ele
'''
def search_academic_users_by_email(email:str):
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
            raise EmptyResultSet
    except ObjectDoesNotExist as e:
       
        return False
    except EmptyResultSet as e:
      
        return False
    except MultipleObjectsReturned as e:
        
        return False
    except OperationalError as e:
        
        return False
    finally:
        if conn is not None:
            cursor.close()
            conn.close()

'''
Busca o objeto de usuario academico no banco de dados e devolve ele
'''
def search_students_by_email(email:str):
    # TODO 
   
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            cursor.execute("select ")
            student=cursor.fetchall()
           
            if(student):
                dictonary_student={
                  'RA':None,
                  'name':None,
                  'year_of_entry':None,
                  'fk_course':None,
                  'password':None,
                }
                for items in student:
                    
                    dictonary_student={
                    'RA':items[0],
                    'name':items[1],
                    'year_of_entry':items[2],
                    'fk_course':items[3],
                    'password':items[4],
                     }
                return dictonary_student
            else:
                return False
        else:
            raise EmptyResultSet
    except ObjectDoesNotExist as e:
       
        return False
    except EmptyResultSet as e:
      
        return False
    except MultipleObjectsReturned as e:
        
        return False
    except OperationalError as e:
        
        return False
    finally:
        if conn is not None:
            cursor.close()
            conn.close()


'''
Puxa as salas que professor X dá aula e pode acessar e ver no dashboard
'''
def professor_get_classes(request):
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
def principal_get_classes(request):
   
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
def academic_users_search_classes_by_classname(request,classname:str):
    academic_user_id=request.session.get("id")
    conn,cursor=None,None
    if(academic_user_id):
        permissions=request.session.get("permissions")
        if("Prof" in permissions):
            try:
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
            except OperationalError:
               messages.error(request,"Houve um erro na conexão com o banco de dados!")
               return False
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()

        elif("Princ" in permissions):
            try:
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
            except OperationalError:
               messages.error(request,"Houve um erro na conexão com o banco de dados!")
               return False
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()
    else:
        messages.error(request,"A autenticação falhou!")
        return False
'''
Busca aulas pelo nome do professor e pela instituição do diretor
'''
def academic_users_search_classes_by_professorname(request,professorname:str):

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

    except OperationalError:
        messages.error(request,"Houve um erro na conexão com o banco de dados!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()



'''
Quando o responsável com auth="Princ" quiser criar um aluno,essa função irá buscar os cursos disponíveis na instituição
'''

def principal_std_creation_courses(request):
    
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
Cria o estudante,com suas aulas iniciais e aulas "faltantes"
Código relativamente complexo, será explicado passo a passo
'''
def principal_std_creation_operation(request,password:str,name:str,valid_ra:str,valid_course:str):
    conn,cursor=None,None #Inicializa as variaveis de conexao
    try:
        conn,cursor=f.connection_cursor() #conecta com o servidor
        hashed_password=f.generate_hash(password) #Faz o Hashing da senha já validada na def std_creation_operation
        if(hashed_password):

            cursor.execute('insert into students("RA",name,year_of_entry,fk_course,password,fk_institution)values(%s,%s,%s,%s,%s,%s)',
                        [valid_ra,name,f.get_year(),valid_course,hashed_password,request.session.get("institution")])
            conn.commit() #Cria o estudante com o RA,nome,curso e senha validados,além de ser vinculado à instituição do criador

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

            cursor.execute(insert_into_classes_actual_str)
            conn.commit()
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
            
            cursor.execute(insert_into_classes_missing_str)
            conn.commit() #Fez a mesma operação já descrita acima
            return True # retorna verdadeiro caso o dê tudo certo
                
    except TypeError: 
        messages.error(request,"Erro na submissão do formulário!")
        return False  
    except OperationalError:
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except errors.UniqueViolation:
        messages.error(request,"Erro na submissão do formulário!")
        return False  
    except errors.UndefinedParameter:
        messages.error(request,"Erro na submissão do formulário!")
        return False  
    except Exception:
        messages.error(request,"Erro desconhecido!")
        messages.error(request,f"Erro{Exception}")
        
        return False
    finally:
        if conn is not None:
            conn.close()
        if cursor is not None:
            cursor.close()

      
