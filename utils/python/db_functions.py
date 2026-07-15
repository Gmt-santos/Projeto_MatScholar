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
def delete_cache_key(request,key:str):
    try:
        cache.delete(key=key)
        
    except r_exceptions as exception:
        messages.error(request,"Erro na operação com o cache!")
        
'''
Faz um rollback das operações de conn de maneira segura
'''
def safe_rollback(conn)->None:
    try:
        conn.rollback()
    except Exception:
        pass
'''
Gera RAs e verifica se eles existem no banco de dados,caso não,retorna o RA
'''
def generate_RA(request)-> str:
    from matscholar_app.models import students
    import random
    try:
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
    except Exception as e:
        raise e
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

    except Exception as e:
            f.receive_exceptions_and_deal(request,type(e).__name__)
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
        
    except Exception as e:
            f.receive_exceptions_and_deal(request,type(e).__name__)
            return False

'''
Valida o academic_user_id enviado na criação de salas (redundante)
'''
def validate_academic_user(request,academic_user_id)->bool:
    from matscholar_app.models import academic_users
    try:
       is_valid=academic_users.objects.filter(fk_institution=request.session.get("institution"),id=academic_user_id).exists()
       return is_valid
    
    except Exception as e:
            f.receive_exceptions_and_deal(request,type(e).__name__)
            return False



