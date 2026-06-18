from . import db_functions
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
    from django.contrib import messages
    try:

        HOST,USER,PASSWORD,DATABASE,PORT=return_dotenv()
        conn=psycopg2.connect(database=DATABASE,user=USER,password=PASSWORD,host=HOST,port=PORT)
        cursor=conn.cursor()
        return conn,cursor
    except psycopg2.OperationalError:
        return False
    #TODO--> erros

'''
Retorna uma String que possa ser utilizada em uma query SQL
'''
def string_to_querylike(string:str):
    return "%"+string+"%"
'''
Valida a entrada de nomes de salas e pessoas
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_query_entries(entry:str):
    import re as regex
    regex_entry:list=regex.findall(r"^[a-zA-ZÀ-ú0-9\'\-\s]+$",entry)
    return regex_entry

'''
Valida a entrada de números positivos
Utilizar somente após ter validado se entry é um número
'''
def validate_strictpositive_numbers_entries(entry:str):
    if(int(entry) <=0):
        return False
    else:
        return True
'''
Valida a entrada de siglas/acrônimos
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''

def validate_acronym_entries(entry:str):
    import re as regex
    regex_entry=regex.findall(r"^[a-zA-ZÀ-ú.]+",entry)
    return regex_entry
        
'''
Valida a entrada de ids em selects e outras entradas que só permitem números
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_ids_entries(entry:str):
    import re as regex
    regex_entry:list=regex.findall(r"^[0-9]+$",entry)
    return regex_entry
'''
Valida a entrada de senhas no login
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_passwords_entries(entry:str):
    import re as regex
    regex_entry:list=regex.findall(r'^[0-9a-zA-Z!@#$*()_]{10,}$',entry)
    return regex_entry

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
Função que gera um hashing de senha --> Utilizado na criaçao de estudantes

'''
def generate_hash(string:str):
    from argon2 import PasswordHasher,exceptions
    try:
         ph=PasswordHasher()
         return ph.hash(string)   
    except exceptions.HashingError:
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
Gera uma senha segura
'''
def generate_safe_password():
    import secrets
    list_chars_lower=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    list_chars_upper=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    list_chars_numbers=['1','2','3','4','5','6','7','8','9','0']
    list_chars_special=['!','@','#','$','*','(',')','_']
    secret_password=""
    secret_password+=(secrets.choice(list_chars_lower))
    secret_password+=(secrets.choice(list_chars_upper))
    secret_password+=(secrets.choice(list_chars_numbers))
    secret_password+=(secrets.choice(list_chars_special))
    for i in range(0,8):
        choice=secrets.randbelow(4)
        match choice:
            case 0:
                 secret_password+=(secrets.choice(list_chars_lower))
            case 1:
                secret_password+=(secrets.choice(list_chars_upper))
            case 2:
                secret_password+=(secrets.choice(list_chars_numbers))
            case 3:
                secret_password+=(secrets.choice(list_chars_special))
    return secret_password

'''
Retorna o ano no qual o usuário está
'''
def get_year():
    import datetime 
    date_obj=datetime.date.today()
    return date_obj.year   

