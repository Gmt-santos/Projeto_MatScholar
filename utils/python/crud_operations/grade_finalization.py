from .. import functions as f
from .. import db_functions as dbf
from . import read
from psycopg2 import OperationalError,errors,DatabaseError
from django.contrib import messages
from psycopg2.extras import execute_values
def get_and_validate_academic_user_password_grade_finalization(request,conn,cursor):
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

def get_all_open_classes_grade_finalization(request,course_id,operation=None,conn=None,cursor=None):
    try:
        if not(conn and cursor):
            conn,cursor=f.connection_cursor()
        if conn and cursor:
            if operation:
                
                cursor.execute("select cls.id,cls.name from classes as cls join classes_courses as cls_crs" \
                " on cls.id=cls_crs.id_class join courses as crs on cls_crs.id_course=crs.id " \
                "where cls_crs.id_course=%s and crs.fk_institution=%s and crs.id=%s and cls.open=1 and cls.abstract=0",
                [course_id,request.session.get("institution"),course_id])
                open_classes_query=cursor.fetchall()
                if open_classes_query:
                   return open_classes_query
                else:
                    messages.error(request,"Não há salas abertas no curso escolhido!")
                    return False
                    
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
                    return False
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False

    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        return False
def get_attendance_students(request,conn,cursor,open_classes):
    try: 
        if conn and cursor:
            listof_dict_attendance=[]

            # Percorre cada tupla de salas abertas
            for i in range (0,len(open_classes)):

                # Puxa para cada sala os dados de presença e ausência dos estudantes
                cursor.execute('select std_cls.id_student,std_cls.attendance,std_cls.absence from' \
                ' students_classes_actual as std_cls' \
                ' join classes as cls on std_cls.id_class=cls.id where cls.id =%s',[open_classes[i][0]])
                attendance_by_student=cursor.fetchall()

                dict_student={} #Cria um dicionário pra sala pesquisada

                # Percorre cada tupla recebida acima,com RA,presenças e ausências
                for std in attendance_by_student:
                     
                     # Adiciona como chave o RA do estudante e como valor a presença em formato decimal
                     dict_student.update({f'{std[0]}':f.get_attendance_rate(std[1],std[2],False)})
                
                # Adiciona esse dicionário para a lista, na mesma ordem da lista open_classes recebida
                listof_dict_attendance.append(dict_student)
                # Faz o loop para as próximas salas

         
            if not listof_dict_attendance:
                messages.error(request,"Não foi possível obter os dados de frequência das salas!")


            # Retorna o dicionário que une RA com presença para cada sala de open_classes
            return listof_dict_attendance
        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")

            return False

    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        return False

def get_all_assignments_students_and_set_grades(request,conn,cursor,open_classes):
    try:
        if conn and cursor:
            listof_assignments_by_class=[]
            listof_assignments_weights=[]
            listof_dict_grades_students=[]
            listof_RA=[]

            # Percorre cada sala de open_classes
            for cls in open_classes:
                # Pesquisa todas as tarefas dos estudantes relacionadas a sala cls
                cursor.execute("select ass_std.fk_student,ass_std.grade * ass.weight from assignments_students as ass_std" \
                " join assignments as ass on ass_std.fk_assignment=ass.id where ass.fk_class=%s",[cls[0]])
                ass_std=cursor.fetchall()

                if ass_std:
                     
                     #  Adiciona o conjunto de tarefas a lista, na mesma ordem de open_classes
                    listof_assignments_by_class.append(ass_std)

                     # Pesquisa a soma dos pesos das tarefas relacionadas a essa sala
                    cursor.execute("select sum(weight)from assignments where fk_class= %s",[cls[0]])
                    pesos=f.regex_list_to_string(cursor.fetchone())

                    if pesos:
                          
                        # Adiciona na lista o peso calculado,  na mesma ordem de open_classes 
                        listof_assignments_weights.append(float(pesos))

                    else:
                         messages.error(request,"Não foi possível obter todos os dados das tarefas!")
                         return False,False
                else:
                    messages.error(request,"Não foi possível obter todos os dados das tarefas!")
                    return False,False
                

            # Depois de pesquisar todos os conjuntos de tarefas relacionadas a open_classes,
            # percorre essa lista criada, criando dicts de par RA com nota
            for cls in listof_assignments_by_class:
                    
                    dict_students={}

                    for assignment in cls:
                        # assignment[0] = RA
                        # assignment[1]= nota já multiplicada pelo peso

                        # Se o RA não estiver na lista de RA, adiciona ele
                        if assignment[0] not in listof_RA:
                             listof_RA.append(assignment[0])
                        
                        # Se a chave do RA não estiver no dict,adiciona o par RA com nota
                        if not dict_students.get(f"{assignment[0]}"):
                             dict_students.update({f'{assignment[0]}':assignment[1]})

                        else:
                             # Se a chave já estiver, só soma as notas
                             dict_students[f'{assignment[0]}']+=assignment[1]

                    # Adiciona o dict criado com as notas, na mesma ordem de open_classes
                    listof_dict_grades_students.append(dict_students)


            # Recebe uma lista de dicionários de par RA com taxa de frequência, na mesma ordem de open_classes
            listof_attendance=get_attendance_students(request,conn,cursor,open_classes)
            universal_absence_limit=read.get_universal_absence_limit(request,conn,cursor)


            if listof_attendance and universal_absence_limit:

                listof_insertions=[]
                listof_deletions=[]
                # Percorre os dicionarios criados na mesma ordem de open_classes pra criar uma tupla no
                # formato de final_grades e uma tupla para deletar de students_classes_missing quem passou
          
                for i in range(0,len(listof_dict_grades_students)):
                    for RA in listof_RA:
                        attendance=listof_attendance[i].get(f"{RA}")
                        grade=listof_dict_grades_students[i].get(f"{RA}")
                        if grade and attendance:   
                            grade=float(grade)
                            final_grade=grade/listof_assignments_weights[i]
                            result=f.avaliate_class_result(
                            final_grade,attendance,universal_absence_limit)
                            
                            if result == "Aprovado":
                               
                                listof_deletions.append((RA,open_classes[i][1],request.session.get("actual_course")))

                            listof_insertions.append(
                            (f'{RA}-{open_classes[i][0]}',RA,open_classes[i][0],attendance,final_grade,result,f.date_to_string(f.get_today_date()))
                            )
                        else:
                            pass
                    
               
                return listof_insertions,listof_deletions

        else:
            messages.error(request,"Houve um erro com a conexão ao banco de dados!")
            return False,False

    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        return False,False
def insert_into_final_grades(request,conn,cursor,listof_insertions):
    try:
        if conn and cursor:

            execute_values(cursor,
            'insert into final_grades(id,id_student,id_class,final_attendance,final_grade,result,operation_date) values %s',
            listof_insertions)
            return True
        else:
            messages.error(request,'Houve um erro com a conexão ao banco de dados!')
            return False
    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        dbf.safe_rollback(conn)
        return False,False


def delete_approved_students_classes_missing(request,conn,cursor,listof_deletions):
     try:
        if conn and cursor:
            for tupla in listof_deletions:
              
                cursor.execute("delete from students_classes_missing where id= any(" \
                "select std_cls_missing.id from students_classes_missing as std_cls_missing join classes as cls" \
                " on std_cls_missing.id_class=cls.id join classes_courses as cls_crs on cls.id=cls_crs.id_class where" \
                " cls.abstract=1 and open=0 and std_cls_missing.id_student=%s and cls.name=%s and cls_crs.id_course=%s)",
                [tupla[0],tupla[1],tupla[2]])
                  
           
            return True
        else:
            messages.error(request,'Houve um erro com a conexão ao banco de dados!')
            return False
     except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        dbf.safe_rollback(conn)
        return False,False

def delete_students_classes_actual(request,conn,cursor,open_classes):
    try:
        if conn and cursor:
            listof_ids=[]
            for cls in open_classes:
                 listof_ids.append(cls[0])
            cursor.execute("delete from students_classes_actual where id_class = any(%s) returning id",[listof_ids,])
           
            return True
        else:
            messages.error(request,'Houve um erro com a conexão ao banco de dados!')
            dbf.safe_rollback(conn)
            return False
    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        dbf.safe_rollback(conn)
        return False

def soft_delete_classes(request,conn,cursor,open_classes):
    try:
        if conn and cursor:
            listof_ids=[]
            for cls in open_classes:
                listof_ids.append(cls[0])
            cursor.execute("update classes set open=0 where id= any(%s) ",[listof_ids,])
           
            return True
        else:
            messages.error(request,'Houve um erro com a conexão ao banco de dados!')
            dbf.safe_rollback(conn)
            return False
        
    except Exception as e:
        f.receive_exceptions_and_deal(request,type(e).__name__)
        dbf.safe_rollback(conn)
        return False,False   
    

def finalize_grades(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            if  get_and_validate_academic_user_password_grade_finalization(request,conn,cursor):
                
                open_classes_query=get_all_open_classes_grade_finalization(
                     request,request.session.get("actual_course"),True,conn,cursor)
                if open_classes_query:
                    listof_insertions,listof_deletions=get_all_assignments_students_and_set_grades(
                    request,conn,cursor,open_classes_query)
                    if listof_insertions:
                        if (insert_into_final_grades(request,conn,cursor,listof_insertions) and
                            delete_approved_students_classes_missing(request,conn,cursor,listof_deletions) and
                            delete_students_classes_actual(request,conn,cursor,open_classes_query) and
                            soft_delete_classes(request,conn,cursor,open_classes_query)):
                             conn.commit()
                             messages.success(request,"Notas fechadas!")
                             return True
                             
                        else:
                            dbf.safe_rollback(conn)
                            return False
                else:
                    dbf.safe_rollback(conn)
                    return False
            else:
                dbf.safe_rollback(conn)
                return False
        else:
            dbf.safe_rollback(conn)
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
    