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
'''
Recebe uma request com método POST e organiza os dados dela em matrizes. Após isso,valida se os RAs enviados realmente
são daquela sala e depois percorre as matrizes executando updates nos registros que select = 1.
No fim,caso nada dê errado, faz o commit, caso contrário, faz o rollback
'''
def professor_assignments_students_operation(request)->bool:
    conn,cursor=None,None
    try:
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
                    print(listof_RA_from_assignment_query,list_RA)
                    if(sorted(listof_RA_from_assignment_query) == sorted(list_RA)):
                      
                        # 'for' pra validação e organização dos dados
                        for i in range(0,len(list_grades)):
                                if(list_select_update[i] ==  "1"):

                                    is_valid_grade:bool|float =f.validate_grades_and_weights(list_grades[i])
                                    is_valid_feedback:list[str] =f.validate_texts(list_feedbacks[i])
                                    is_valid_RA:list[str]=f.validate_ids_entries(list_RA[i])

                                    if is_valid_feedback and is_valid_grade and is_valid_RA:

                                        cursor.execute('update assignments_students set grade=%s,feedback=%s where'
                                        ' assignments_students.fk_student=%s and assignments_students.fk_assignment=%s',
                                        [abs(is_valid_grade),is_valid_feedback[0],is_valid_RA[0],
                                        request.session.get("actual_assignment_id")])

                                    else:

                                        messages.error(request,"Dado inválido enviado!")
                                        dbf.safe_rollback(conn)
                                        return False
                                    
                                elif(list_select_update[i] == "0"):

                                    pass
                                
                                else:
                                    messages.error(request,"Opção inválida enviada!")
                                    dbf.safe_rollback(conn)
                                    return False
                                
                        conn.commit()
                        messages.success(request,"Alteração feita com sucesso!")
                        return True

                    else:
                        dbf.safe_rollback(conn)
                        messages.error(request,"Os dados dos alunos enviados não pertencem a essa sala!")
                        return False
                else:
                    dbf.safe_rollback(conn)
                    messages.error(request,"Não há alunos nessa sala!")
                    return False
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
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

def professor_attendance_update(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            listof_RA=request.POST.getlist("student_RA")
            listof_attendance=request.POST.getlist("attendance")
            if listof_RA and listof_attendance and len(listof_RA) == len(listof_attendance) and ("1" in listof_attendance
            or "0" in listof_attendance):
                
                students_query=read.professor_attendance_get_all_students_by_class(request,conn,cursor,True)

                if (students_query) and (len(students_query) ==  len(listof_RA)):
                    listof_students_query=[]

                    for tupla in students_query:
                        listof_students_query.append(tupla[0])

                    if(sorted(listof_students_query) == sorted(listof_RA)):

                        for i in range(0,len(listof_RA)):

                            if listof_attendance[i] ==  "1":
                                cursor.execute("update students_classes_actual set attendance=attendance+1 where" \
                                " id_student = %s and id_class = %s",[listof_RA[i],request.session.get("actual_class_id")])
                            elif listof_attendance[i] ==  "0":
                                 cursor.execute("update students_classes_actual set absence=absence+1 where" \
                                " id_student = %s and id_class = %s",[listof_RA[i],request.session.get("actual_class_id")])
                            else:
                                messages.error(request,"Dado inválido enviado!")
                                dbf.safe_rollback(conn)
                                return False
                            
                        conn.commit()
                        messages.success(request,"Dados registrados com sucesso!")
                        return True
                    
                    else:
                        messages.error(request,"Dado inválido enviado!")
                        return False
                else:
                    messages.error(request,"Dado inválido enviado!")
                    return False
            else:
                messages.error(request,"Dado inválido enviado!")
                return False
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
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

