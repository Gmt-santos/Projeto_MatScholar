

'''
Funções em Python
Serão descritas antes de sua definição
'''
'''
Retornar as variaveis do .env
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
    except psycopg2.errors 

'''
Busca o objeto de usuario academico no banco de dados e devolve ele
'''
def search_academic_users_by_email(email:str):
    from django.core.exceptions import ObjectDoesNotExist,EmptyResultSet,MultipleObjectsReturned
    from matscholar_app.models import academic_users_permissions,academic_users
    try:
        conn,cursor=connection_cursor()
        cursor.execute("select academic_users.id,academic_users.name,academic_users.role,academic_users.email,academic_users.password,academic_users.fk_institution,"
        "permissions.nickname from academic_users join academic_users_permissions on academic_users.id=academic_users_permissions.id_user join"
        " permissions on academic_users_permissions.id_nickname=permissions.id")
        if(academic_user):
            return academic_user
        ##    TODO  ##
    except ObjectDoesNotExist:
        return False
    except EmptyResultSet:
        return False
    except MultipleObjectsReturned:
        return False
'''
Verifica se a senha enviada por POST é igual a senha do banco
'''
def verify_hashed(password_POST:str,academic_user):
    from argon2 import PasswordHasher,exceptions
    try:
        ph=PasswordHasher()
        ph.verify(academic_user.password,password_POST)
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
              

