from .. import functions as f
from .. import db_functions as dbf
from . import read
from psycopg2 import OperationalError,errors,DatabaseError
from django.contrib import messages
from psycopg2.extras import execute_values
def get_and_validated_academic_user_password_grade_finalization(request,conn,cursor):
    try:
        cursor.execute("select a_users.password from academic_users as a_users where a_users.id=%s " \
        "and a_users.fk_institution=%s",[request.session.get("id"),request.session.get("institution")]) 
        password_db=f.regex_list_to_string(cursor.fetchone())
        if password_db:
            if f.verify_hashed(request.POST.get("password"),password_db):
                return True
            else:
                messages.error(request,"Senha incorreta!")
                return False
        else:
            messages.error(request,"O usuário não foi autorizado a fazer essa operação!")
            return False
      
    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        return False

def get_all_classes_grade_finalization(request,course_id,operation=None,conn=None,cursor=None):
    try:
        if not(conn and cursor):
            conn,cursor=f.connection_cursor()
        if conn and cursor:
            if operation:
                pass
            else:
                cursor.execute("select cls.name,cls.start_date,cls.end_date,a_users.role,a_users.name from classes as cls" \
                " join academic_users as a_users on cls.fk_professor = a_users.id join classes_courses as cls_crs" \
                " on cls.id=cls_crs.id_class where cls_crs.id_course=%s and a_users.fk_institution=%s and cls.open=1 and"
                " cls.abstract=0 ",
                [course_id,request.session.get("institution")])
                open_classes_query=cursor.fetchall()
                if open_classes_query:
                    listof_open_classes_dict=[]
                    for tupla in open_classes_query:
                        listof_open_classes_dict.append({
                            'class_name':tupla[0],
                            'class_start_date':tupla[1],
                            'class_end_date':tupla[2],
                            'prof_role':tupla[3],
                            'prof_name':tupla[4],
                        })
                    return listof_open_classes_dict
                else:
                    messages.error(request,"Não há salas abertas no curso escolhido!")
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False

    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        return False



def finalize_grades(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            pass
        # TODO--Finalizar
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False
    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    pass