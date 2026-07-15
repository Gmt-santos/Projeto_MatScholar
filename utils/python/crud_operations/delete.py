from .. import functions as f
from .. import db_functions as dbf
from psycopg2 import OperationalError,errors,DatabaseError
from django.contrib import messages

'''
Deleta uma sala e todos os seus registros relacionados,como tarefas,notas,alunos-sala e seu registro no cache
'''
def principal_cls_edition_delete_class(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            cursor.execute("delete from final_grades where id_class = %s",[request.session.get("actual_class_id"),])
            cursor.execute("delete from classes_courses where id_class=%s returning id_course",
            [request.session.get("actual_class_id"),])
            course_id=cursor.fetchone()[0]
            cursor.execute("delete from students_classes_actual where id_class= %s",[request.session.get("actual_class_id"),])
            cursor.execute('delete from assignments_students where fk_assignment = any(' \
            'select id from assignments where fk_class=%s) ',[request.session.get("actual_class_id"),])
            cursor.execute('delete from assignments where fk_class=%s',[request.session.get("actual_class_id")])
            cursor.execute("delete from classes where id = %s ",[request.session.get("actual_class_id"),])
            
            dbf.delete_cache_key(request,f"open_classes:{course_id}-{request.session.get("institution")}")
            dbf.delete_cache_key(request,f"institution_id_classes:{request.session.get("institution")}")
            conn.commit()
            del request.session["actual_class_id"]
            messages.success(request,"Aula excluída com sucesso!")
            return True
            
        else:
            messages.error(request,"Houve um erro com a conexão do banco de dados!")
            return False
        
    except Exception as e:
            f.receive_exceptions_and_deal(request,type(e).__name__)
            dbf.safe_rollback(conn)
            return False
    
    finally:
       
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


'''
É a operação de exclusão de um estudante com sua sala,exclui os
relacionamentos assignments,final_grades e students_classes_actual
'''
def principal_cls_edition_del_students(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            list_RA=request.POST.getlist("students_RA")
            list_opt_del=request.POST.getlist("students_opt_del")
            list_del_RA=[]
            if len(list_RA)==len(list_opt_del):
                if "1" not in list_opt_del:
                    return True
                for i in range(0,len(list_RA)):

                    if f.validate_ids_entries(list_RA[i]):

                        if list_opt_del[i] == "1":
                            list_del_RA.append(list_RA[i])


                        elif list_opt_del[i] != "0":
                            messages.error(request,"Algum dado inválido foi enviado!")
                            return False

                    else:
                        messages.error(request,"Algum dado inválido foi enviado!")
                        return False

                cursor.execute('delete from final_grades where id_student =any(%s) and id_class=%s',
                               [list_del_RA,request.session.get("actual_class_id")])
                cursor.execute('delete from assignments_students where fk_student=any(%s) and fk_assignment = any(' \
                'select assignments.id from assignments where fk_class=%s)',[list_del_RA,request.session.get("actual_class_id")])
                cursor.execute('delete from students_classes_actual where id_class=%s and id_student in(select "RA" ' \
                'from students where students.fk_institution = %s and students."RA" = any(%s)) returning id_student',
                [request.session.get("actual_class_id"),request.session.get("institution"),list_del_RA])
                if(len(cursor.fetchall()) == len(list_del_RA)):
                    conn.commit()
                    return True
                else:
                    dbf.safe_rollback(conn)
                    return False


            else:

                messages.error(request,"Algum dado inválido foi enviado!")
                return False


        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False
        
    except Exception as e:
            f.receive_exceptions_and_deal(request,type(e).__name__)
            dbf.safe_rollback(conn)
            return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
'''
Deleta a tarefa e todos os relacionamentos dos estudantes com ela
'''
def professor_del_assignment(request,password:str):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        
        if conn and cursor:
            cursor.execute("select password from academic_users join classes on academic_users.id=classes.fk_professor " \
            "join assignments on classes.id=assignments.fk_class where" \
            " academic_users.id = %s and classes.id= %s and assignments.id =%s",[request.session.get("id"),
            request.session.get("actual_class_id"),request.session.get("actual_assignment_id")])
            password_db=cursor.fetchone()
            if password_db:
                if(f.verify_hashed(password,password_db[0])):

                    cursor.execute("delete from assignments_students where fk_assignment = any(" \
                    "select ass.id from assignments as ass join classes as cls on ass.fk_class=cls.id where ass.id=%s and" \
                    " cls.id=%s and cls.fk_professor=%s)",[request.session.get("actual_assignment_id"),
                    request.session.get("actual_class_id"),request.session.get("id")])
                    cursor.execute("delete from assignments where id= any(" \
                    "select ass.id from assignments as ass join classes as cls on ass.fk_class=cls.id where ass.id=%s and" \
                    " cls.id=%s and cls.fk_professor=%s)",[request.session.get("actual_assignment_id"),
                    request.session.get("actual_class_id"),request.session.get("id")])
                    conn.commit()
                    del request.session['actual_assignment_id']
                    messages.success(request,"Tarefa excluída com sucesso!")
                    return True
                else:
                    messages.error(request,"Senha incorreta!")
                    return False
            else:
                messages.error(request,"A tarefa selecionada não existe ou o usuário não tem acesso a ela!")
                return False

        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False
        
    except Exception as e:
            f.receive_exceptions_and_deal(request,type(e).__name__)
            dbf.safe_rollback(conn)
            return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()