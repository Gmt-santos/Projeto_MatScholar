from .. import functions as f
from .. import db_functions as dbf
from psycopg2 import OperationalError,errors,DatabaseError
from django.contrib import messages


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
def principal_std_edition_operation(request):
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


