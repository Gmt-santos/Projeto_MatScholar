

'''
Funções em Python
Serão descritas antes de sua definição
'''
'''
Retornar as variaveis do .env----> Apenas utilizada na função "connection_cursor"
'''
def return_dotenv():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    return os.environ.get("HOST"),os.environ.get("USER"),os.environ.get("PASSWORD"),os.environ.get("DATABASE"),os.environ.get("PORT")
'''
Retornar uma conexão e um cursor do banco (USE SOMENTE EM OPERAÇÕES NÃO TRIVIAIS)
'''
def connection_cursor():
    import psycopg2
    try:

        HOST,USER,PASSWORD,DATABASE,PORT=return_dotenv()
        conn=psycopg2.connect(database=DATABASE,user=USER,password=PASSWORD,host=HOST,port=PORT)
        cursor=conn.cursor()
        return conn,cursor
    except psycopg2.OperationalError:
        return False
    #TODO--> erros

'''
Busca o objeto de usuario academico no banco de dados e devolve ele
'''
def search_academic_users_by_email(email:str):
    from django.core.exceptions import ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned
    from psycopg2.errors import OperationalError
    conn,cursor=None,None
    try:
        conn,cursor=connection_cursor()
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
    from django.core.exceptions import ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned
    from psycopg2.errors import OperationalError
    conn,cursor=None,None
    try:
        conn,cursor=connection_cursor()
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
Verifica se a senha enviada por POST é igual a senha do banco
'''
def verify_hashed(password_POST:str,academic_user:dict):
    from argon2 import PasswordHasher,exceptions
    try:
        ph=PasswordHasher()
        ph.verify(academic_user["password"],password_POST)
        return True
    except exceptions.VerifyMismatchError:
      
        return False
'''
Caso o usuario erre o email,faz um hashing generico pra evitar timing attacks
'''
def hashing_false():
    from argon2 import PasswordHasher,exceptions
    try:
        ph=PasswordHasher()
        ph.hash("blablabla123")
        return True
    except exceptions.VerifyMismatchError:
        return False
'''
Verifica se o email é válido com base no padrão rfc 5322
'''
def email_validation(email:str):
    import re as re
    regex_email_compiled=re.compile("^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$")
    is_valid=regex_email_compiled.search(email)
    return is_valid
              
'''
Coloca os dados puxados no banco para a sessão para evitar sobrecarregar o banco com querys desnecessárias
'''
def academic_users_set_session_attributes(request,dictionary:dict):
    request.session["id"]=dictionary["id"]
    request.session["name"]=dictionary["name"]
    request.session["role"]=dictionary["role"]
    request.session["email"]=dictionary["email"]
    request.session["institution"]=dictionary["fk_institution"]
    request.session["permissions"]=dictionary["permissions_nicknames"]

def students_set_session_attributes(request,dictionary:dict):
    # request.session["id"]=dictionary["id"]
    # request.session["name"]=dictionary["name"]
    # request.session["role"]=dictionary["role"]
    # request.session["email"]=dictionary["email"]
    # request.session["institution"]=dictionary["fk_institution"]
    # request.session["permissions"]=dictionary["permissions_nicknames"]
    return True
# TODO #

'''
Puxa as salas que professor X dá aula e pode acessar e ver no dashboard
'''
def professor_get_classes(request):
    from matscholar_app.models import classes
    from django.core.cache import cache
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
Disponibiliza no Dashboard
'''
def principal_get_classes(request):
    from django.core.cache import cache
    from psycopg2 import OperationalError
    from redis import exceptions as r_exceptions
    from django.contrib import messages
    conn,cursor=None,None
    try:

        conn,cursor=connection_cursor()
        institution_id=request.session.get("institution")
        principal_id=request.session.get("id")
        if institution_id and principal_id:
            if(cache.get(f"principal_id_classes:{institution_id},{principal_id}")):
                classes_query=cache.get(f"principal_id_classes:{institution_id},{principal_id}")
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
                    cache.set(f"principal_id_classes:{institution_id},{principal_id}",lista,timeout=1200)
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

def search_classes_by_classname(request,classname:str):
    from psycopg2 import OperationalError
    academic_user_id=request.session.get("id")
    conn,cursor=None,None
    if(academic_user_id):
        permissions=request.session.get("permissions")
        if("Prof" in permissions):
            try:
                conn,cursor=connection_cursor()
                cursor.execute("")
            except:
            finally:
                if cursor is not None:
                    cursor.close()
                if conn is not None:
                    conn.close()