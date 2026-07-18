from . import db_functions
from datetime import datetime
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
def string_to_querylike(string:str)->str:
    return "%"+string+"%"
'''
Valida a entrada de nomes de salas
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_query_entries(entry:str)->list[str]:
    import re as regex
    regex_entry:list=regex.findall(r"^[a-zA-ZÀ-ú0-9\'\-\s.]+$",entry)
    return regex_entry
'''
Valida a entrada de nomes de pessoas
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_name_entries(entry:str)->list[str]:
    import re as regex
    regex_entry:list=regex.findall(r"^[a-zA-ZÀ-ú\'\-\s]+$",entry)
    return regex_entry
'''
Valida a entrada de números positivos
Utilizar somente após ter validado se entry é um número
'''
def validate_strictpositive_numbers_entries(entry:str)->bool:
    try:

        if(int(entry) <=0):
            return False
        else:
            return True
    except Exception:
        return False
'''
Valida a entrada de siglas/acrônimos
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''

def validate_acronym_entries(entry:str)->list[str]:
    import re as regex
    regex_entry=regex.findall(r"^[a-zA-ZÀ-ú.]+",entry)
    return regex_entry
        
'''
Valida a entrada de ids em selects e outras entradas que só permitem números
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_ids_entries(entry:str)->list[str]:
    import re as regex
    regex_entry:list=regex.findall(r"^[0-9]+$",entry)
    return regex_entry
'''
Valida a entrada de senhas no login
RETORNA UMA LISTA ----> SEMPRE UTILIZAR var[0]
'''
def validate_passwords_entries(entry:str)->list[str]:
    import re as regex
    regex_entry:list=regex.findall(r'^[0-9a-zA-Z!@#$*()_]{10,}$',entry)
    return regex_entry

'''
Verifica se a senha enviada por POST é igual a senha do banco
'''
def verify_hashed(password_POST:str,password_db:str):
    from argon2 import PasswordHasher,exceptions
    try:
        ph=PasswordHasher()
        ph.verify(password_db,password_POST)
        return True
    except exceptions.VerifyMismatchError:
      
        return False
'''
Caso o usuario erre o email,faz um hashing generico
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
def academic_users_set_session_attributes(request,dictionary:dict)->None:
    request.session["id"]=dictionary["id"]
    request.session["name"]=dictionary["name"]
    request.session["role"]=dictionary["role"]
    request.session["email"]=dictionary["email"]
    request.session["institution"]=dictionary["fk_institution"]
    request.session["permissions"]=dictionary["permissions_nicknames"]

def students_set_session_attributes(request,dictionary:dict):
    request.session["RA"]=dictionary["RA"]
    request.session["name"]=dictionary["name"]
    request.session["year_of_entry"]=dictionary["year_of_entry"]
    request.session["course"]=dictionary["fk_course"]
    request.session["institution"]=dictionary["fk_institution"]
   

'''
Gera uma senha segura
'''
def generate_safe_password()->str:
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
Recebe a quantidade de presenças e faltas e retorna a string ou decimal da porcentagem de presença.
'''
def get_attendance_rate(attendance:int,absence:int,return_string:bool)-> str|float:
    try:
        if return_string:

            return "{attendance_rate:.2f}%".format(attendance_rate=( ( attendance/(attendance+absence) ) * 100 ))
        else:
            return float( ( attendance/(attendance+absence) )  )
        
    except ZeroDivisionError:
        if return_string:
            return "0%"
        else:
            return 0


'''
Retorna o ano no qual o usuário está
'''
def get_year():
    import datetime 
    date_obj=datetime.date.today()
    return date_obj.year   
'''
Retorna a data no qual o usuário está e pode usar também o dia anterior caso esteja sendo feita uma busca pela data futura de
algum campo
'''
def get_today_date(deadline_comparison=False):
    import datetime
    if deadline_comparison:
        date_obj=datetime.date.today()-datetime.timedelta(days=1)
    else:
        date_obj=datetime.date.today()
    return date_obj
'''
Recebe uma lista de tuplas e transforma em uma lista de dicts
Usada na criação de salas pelo "Princ"
'''
def generate_academic_users_query_listofdict(academic_users_query)->list[dict]:
    lista_dicts:list[dict]=[]
    for tupla in academic_users_query:
        lista_dicts.append({
            "id":tupla[0],
            "name":tupla[1],
        })
    return lista_dicts
def generate_student_query_listofdict(students_query)->list[dict]:
    lista_dicts:list[dict]=[]
    for tupla in students_query:
        lista_dicts.append({
            "RA":tupla[0],
            "name":tupla[1],
        })
    return lista_dicts
'''
Verifica se a data enviada é válida, ou seja, é uma data futura ou atual
'''
def validate_date(date)->str|bool:
    from datetime import datetime,timedelta
    try:
        today=datetime.today()
        date_format=datetime.strptime(date,"%Y-%m-%d")
        
        if date_format >= today-timedelta(days=1):
            return date
        else:
            return False
    except Exception:
        return False
'''
Tranforma um objeto do tipo date em uma string
(Usado mais no frontend)
'''
def date_to_string(date)->str:
    from datetime import datetime
    str_date=date.strftime("%Y-%m-%d")
  
    return str_date

'''
Verifica se a data de fim de uma aula vem depois da data de inicio, além de verificar se ambas sao futuras
'''
def validate_start_end_date(start_date,end_date):
    try:
        from datetime import datetime
        today=datetime.today()
        start_date_format=datetime.strptime(start_date,"%Y-%m-%d")
        end_date_format=datetime.strptime(end_date,"%Y-%m-%d")
        if end_date_format > start_date_format and end_date_format>today and start_date_format>today:
            return start_date,end_date
        else:
            return False,False
    except Exception:
        return False,False
'''
Recebe uma lista de tuplas de assignments e transforma ela em uma lista de dicts
Usada pelo usuário com permissão de professor
(Parâmetro já verificado no caso venha vazio)
'''
def generate_assignments_listof_dict(assignments_students_query:list[tuple])->list[dict]:
    listof_dict=[]
    for tuple in assignments_students_query:
        listof_dict.append(
            {
                'student_RA':tuple[0],
                'student_name':tuple[1],
                'student_grade':tuple[2],
                'professor_feedback':tuple[3],
            }

        )
    return listof_dict

'''
Valida a entrada de notas e pesos
Usada nos assignments
'''
def validate_grades_and_weights(entry:str)-> float|bool:
    import re as regex
    try:
        
        regex_entry:list[str]=regex.findall(r"^[0-9]{1,3}[,.]{0,1}[0-9]{0,2}$",entry)
        
        if(regex_entry):
            regex_entry_float=float(regex_entry[0].replace(',','.'))    
            return regex_entry_float
        else:
            
            return False
    except Exception :
       
        return False
    
'''
Valida a entrada de textos
Usada nos assignments
Retorna uma lista, então use regex_entry[0] no retorno da função
'''
def validate_texts(entry:str)->list[str]:
    import re as regex
    regex_entry:list[str]=regex.findall(r"^[0-9a-zA-ZÀ-ú\s!.()?%$#@/\\:=+-{}]+$",entry,flags=regex.MULTILINE)

    return regex_entry

'''
Recebe as listas vindas do regex ou dos fetches(grade finalization) e retorna a string encontrada ou o valor False
'''
def regex_list_to_string(regex_list:list)->str|bool:
    if regex_list:
        return regex_list[0]
    else:
        return False
    



'''
Recebe exceções e trata elas de acordo com o caso
Recebe type(raised_exception).__name__ e a request
'''
def receive_exceptions_and_deal(request,exception_name):
    from django.contrib import messages
    match(exception_name):
        case "ConnectionError":
            messages.error(request,"Houve um erro com a conexão ao cache!")

        case "TimeoutError":
            messages.error(request,"Tempo de consulta ao cache expirado!")

        case "InvalidTextRepresentation" |'NameTooLong'\
        |'DatatypeMismatch'|'DataError'|'NumericValueOutOfRange'|'NullValueNotAllowed'\
        |'InvalidDatetimeFormat'|'DatetimeFieldOverflow'|'DataError'|'InvalidForeignKey'|'FloatingPointException':
            messages.error(request,'Dado incompatível com o banco de dados enviado!')

        case 'IntegrityConstraintViolation'|'RestrictViolation'|'NotNullViolation'\
            |'ForeignKeyViolation'|'UniqueViolation'|'CheckViolation'|'ExclusionViolation'|'IntegrityError':
            messages.error(request,'Operação invalidada pelas regras de negócio!')

        case 'InsufficientResources'|'DiskFull'|'OutOfMemory'|'TooManyConnections'|'ConfigurationLimitExceeded':
            messages.error(request,'Tráfego intenso no servidor, a operação não pôde ser executada!')

        case 'ConnectionException'|'SqlclientUnableToEstablishSqlconnection'|'ConnectionDoesNotExist'| \
        'SqlserverRejectedEstablishmentOfSqlconnection'|'ConnectionFailure'|'TransactionResolutionUnknown'|\
        'ProtocolViolation'|'DatabaseError':
            messages.error(request,'Houve um erro com a conexão ao banco de dados!')
        
        case 'OperationalError':
            messages.error(request,"Houve um erro interno no banco de dados, a operação não pôde ser executada")
        
        case 'InternalError_'|'DataCorrupted'|'IndexCorrupted'|'InternalError':
            messages.error(request,'Erro crítico interno, contate o suporte imediatamente!')

        case 'IndexError'|'KeyError':
            messages.error(request,"Houve alguma alteração inválida nas informações enviadas!")

        case 'OverflowError':
            messages.error(request,'O número enviado não pôde ser processado!')

        case 'TypeError'|'ValueError':
            messages.error(request,'Alguma informação enviada é inválida!')

        case 'ZeroDivisionError':
            messages.error(request,'A operação não pôde ser matematicamente executada!')

        case 'ObjectDoesNotExist'|'EmptyResultSet'|'MultipleObjectsReturned':
            messages.error(request,'A operação realizada retornou registros inesperados!')

        case _:
            messages.error(request,f'Erro desconhecido: {exception_name}')
        


        
'''
Recebe uma lista com os pesos e as notas de tarefas de uma determinada sala e retorna a média ponderada
'''
def calculate_gpa(listof_assignments_weight_grade:list[tuple],return_string:bool):
    weights=0
    sum_of_grades=0
    try:
        for tupla in listof_assignments_weight_grade:
            weights+=tupla[0]
            sum_of_grades+=tupla[0]*tupla[1]
        if return_string:
            return "{gpa:.2f}".format(gpa=sum_of_grades/weights)
        else:
            return sum_of_grades/weights
    except ZeroDivisionError:
        return False
    

def avaliate_class_result(grade,attendance,universal_absence_limit):
    if grade >=5 and attendance >=universal_absence_limit:
        return "Aprovado"
    elif grade<5 and attendance < universal_absence_limit:
        return "Reprovado por falta e nota"
    elif grade<5 and attendance>universal_absence_limit:
        return 'Reprovado por nota'
    elif grade>=5 and attendance<universal_absence_limit:
        return 'Reprovado por falta'
    
