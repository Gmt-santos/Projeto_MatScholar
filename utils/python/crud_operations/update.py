from .. import functions as f
from .. import db_functions as dbf
from . import read 
from psycopg2 import OperationalError,errors,DatabaseError
from django.contrib import messages
from psycopg2.extras import execute_values

'''
Atualiza os dados de data de inicio,data de fim e discente/professor da sala escolhida
'''
def principal_cls_edition_update_cls(request):
    conn,cursor=None,None
    try:

        conn,cursor=f.connection_cursor()

        if conn and cursor:

            start_date,end_date=f.validate_start_end_date(request.POST.get("start_date"),request.POST.get("end_date"))
            academic_user_id=f.validate_ids_entries(request.POST.get("academic_user"))

            if start_date and end_date and academic_user_id:

                academic_user_id=academic_user_id[0]

                if(dbf.validate_academic_user(request,academic_user_id)):

                    cursor.execute("update classes set fk_professor=%s,start_date=%s,end_date=%s" \
                    " where id=%s and open=1 and abstract=0",[academic_user_id,start_date,end_date,
                    request.session.get("actual_class_id")])
                    conn.commit()
                    return True
                
                else:

                    messages.error(request,"Professor inválido enviado!")
                    return False
            else:

                messages.error(request,"Data inválida ou professor inválido enviado!")
                return False

        else:
            messages.error(request,"Erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        dbf.safe_rollback(conn)
        messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
        return False
    except errors.UndefinedColumn:
        dbf.safe_rollback(conn)
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        dbf.safe_rollback(conn)
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        dbf.safe_rollback(conn)
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
        if conn:
            dbf.safe_rollback(conn)
        messages.error(request,"Erro desconhecido!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
'''
Atualiza o nome do estudante
'''
def principal_std_edition_operation(request)->bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            valid_name=f.validate_name_entries(request.POST.get("name"))
            if valid_name:
                valid_name=valid_name[0]
                cursor.execute('update students set name = %s where students."RA" = %s and students.fk_institution=%s',
                               (valid_name,request.session.get("actual_student_RA"),request.session.get("institution")))
                conn.commit()
                del request.session["actual_student_RA"]
                return True
            else:
                messages.error(request,"Nome inválido enviado!")
                return False
        else:
            messages.error(request,"Erro com a conexão ao banco de dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        dbf.safe_rollback(conn)
        messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
        return False
    except errors.UndefinedColumn:
        dbf.safe_rollback(conn)
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        dbf.safe_rollback(conn)
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        dbf.safe_rollback(conn)
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
        if conn:
            dbf.safe_rollback(conn)
        messages.error(request,"Erro desconhecido!")
       
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

'''
Atualiza os dados das tarefas criadas pelo professor
"actual_class_id" atribuida em  "professor_cls_edition_get_all_info_classe"
"actual_assignment_id" atribuida em " prof_assignment_view"
'''
def professor_assignment_update_operation(request,name:str,desc:str,deadline:str,weight:float,max_grade:float)->bool:
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
         
            cursor.execute('update assignments set name=%s,"desc"=%s,deadline=%s,weight=%s,max_grade=%s where id = any(' \
            'select ass.id from assignments as ass join classes as cls on ass.fk_class=cls.id where cls.id=%s'
            ' and cls.fk_professor=%s and ass.id=%s) returning id',[name,desc,deadline,weight,max_grade,
            request.session.get("actual_class_id"),request.session.get("id"),request.session.get("actual_assignment_id")])
            if(cursor.fetchone()):
                conn.commit()
                messages.success(request,"Alteração bem sucedida!")
                return True
            else:
                dbf.safe_rollback(conn)
                messages.error(request,"A alteração dessa tarefa não é válida!")
                return False
        else:
            messages.error(request,"Erro com a conexão ao banco de dados!")
            return False

     

    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        dbf.safe_rollback(conn)
        messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
        return False
    except errors.UndefinedColumn:
        dbf.safe_rollback(conn)
        messages.error(request,"Algum dado inválido foi enviado!")
        return False
    except IndexError:
        dbf.safe_rollback(conn)
        messages.error(request,"Alteração no formulário detectada! Operação abortada!")
        return False
    except OperationalError:
        dbf.safe_rollback(conn)
        messages.error(request,"Houve um erro com a conexão do banco de dados!")
        return False
    except Exception as e :
        if conn:
            dbf.safe_rollback(conn)
        messages.error(request,"Erro desconhecido!")
       
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def professor_assignments_students_operation(request)->bool:
        conn,cursor=None,None
    # try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            list_RA:list[str]=request.POST.getlist("student_RA")
            list_grades:list[str]=request.POST.getlist("grade")
            list_feedbacks:list[str]=request.POST.getlist("feedback")
            list_select_update:list[str]=request.POST.getlist("assignment_update")
            if (list_grades and list_feedbacks and  list_select_update and list_RA) and \
            (len(list_grades)== len(list_feedbacks) and len(list_feedbacks) == len( list_select_update) and
            len(list_select_update) == len(list_RA)):
                
                listof_RA_from_assignment_query=read.search_students_by_assignment(request,conn,cursor)

                if(listof_RA_from_assignment_query):

                    if(sorted(listof_RA_from_assignment_query) == sorted(list_RA)):

                        # 'for' pra validação e organização dos dados
                        for i in range(0,len(list_grades)):

                            is_valid_grade:bool|float =f.validate_grades_and_weights(list_grades[i])
                            is_valid_feedback:list[str] =f.validate_texts(list_feedbacks[i])
                            is_valid_RA:list[str]=f.validate_ids_entries(list_RA[i])

                            if is_valid_grade and is_valid_feedback and is_valid_RA :

                                if(list_select_update[i] ==  "1"):
                                    
                                    cursor.execute('update assignments_students set grade=%s,feedback=%s where'
                                    ' assignments_students.fk_student=%s and assignments_students.fk_assignment=%s',
                                    [is_valid_grade,is_valid_feedback[0],is_valid_RA[0],
                                     request.session.get("actual_assignment_id")])
                                    #TODO VALIDAR MAX GRADE
                                elif(list_select_update[i] == "0"):

                                    pass
                                
                                else:
                                    messages.error(request,"Dado inválido enviado!")
                                    dbf.safe_rollback(conn)
                                    return False
                            
                            else:
                                messages.error(request,"Dado inválido enviado!")
                                dbf.safe_rollback(conn)
                                return False
                            
                        conn.commit()
                        messages.success(request,"Alteração feita com sucesso!")
                        return True

                    else:
                        messages.error(request,"Os dados dos alunos enviados não pertencem a essa sala!")
                        return False
                else:
                    messages.error(request,"Não há alunos nessa sala!")
                    return False
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False

            
            
    # except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
    #         DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
    #     dbf.safe_rollback(conn)
    #     messages.error(request,"Alteração indevida no formulário ou erro de envio! ")
    #     return False
    # except errors.UndefinedColumn:
    #     dbf.safe_rollback(conn)
    #     messages.error(request,"Algum dado inválido foi enviado!")
    #     return False
    # except IndexError:
    #     dbf.safe_rollback(conn)
    #     messages.error(request,"Alteração no formulário detectada! Operação abortada!")
    #     return False
    # except OperationalError:
    #     dbf.safe_rollback(conn)
    #     messages.error(request,"Houve um erro com a conexão do banco de dados!")
    #     return False
    # except Exception as e :
    #     if conn:
    #         dbf.safe_rollback(conn)
    #     messages.error(request,"Erro desconhecido!")
       
    #     return False
    # finally:
    #     if cursor is not None:
    #         cursor.close()
    #     if conn is not None:
    #         conn.close()

    