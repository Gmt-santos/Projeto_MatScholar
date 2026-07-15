from .. import functions as f
from .. import db_functions as dbf
from . import read
from psycopg2 import OperationalError,errors,DatabaseError
from django.contrib import messages
from psycopg2.extras import execute_values

'''
Cria o estudante,com suas aulas iniciais e aulas "faltantes"
Código relativamente complexo, será explicado passo a passo
'''
def principal_std_creation_operation(request,password:str,name:str,valid_ra:str,valid_course:str)->bool:
    conn,cursor=None,None #Inicializa as variaveis de conexao
    try:
        conn,cursor=f.connection_cursor() #conecta com o servidor
        hashed_password=f.generate_hash(password) #Faz o Hashing da senha já validada na def std_creation_operation
        if(hashed_password and conn and cursor):

            cursor.execute('insert into students("RA",name,year_of_entry,fk_course,password,fk_institution,graduated)values(%s,%s,%s,%s,%s,%s,0)',
                        [valid_ra,name,f.get_year(),valid_course,hashed_password,request.session.get("institution")])
            #Cria o estudante com o RA,nome,curso e senha validados,além de ser vinculado à instituição do criador

            cursor.execute('select classes.id from classes join classes_courses on classes.id=classes_courses.id_class join ' \
            'courses on classes_courses.id_course=courses.id where classes.open=1 and courses.fk_institution=%s and courses.id=%s and'
            ' classes.initial=1 and abstract=0',
            [request.session.get("institution"),valid_course])
            classes_initial=cursor.fetchall()

            # Busca os Ids das aulas que estão abertas,são iniciais(initial=1),não são abstratas(abstract=0),que tenham o id do curso
            # selecionado(courses.id) e que sejam da instituição do criador(courses.fk_institution)

            if not classes_initial:
                messages.error(request,"O curso não possui salas iniciais!")
                dbf.safe_rollback(conn)
                return False

            insert_into_classes_actual_str="insert into students_classes_actual(id,id_class,id_student,absence,attendance)values"
            #Inicializa uma string para o insert
            for tupla in classes_initial:
                if tupla == classes_initial[-1]:
                    insert_into_classes_actual_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra},0,0);"
                else:
                    insert_into_classes_actual_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra},0,0),"
            # Percorre a lista de tuplas retornada pela busca anterior de Ids das aulas e adiciona esses Ids na string
            # do insert
            '''
            Se o usuário tentar criar um estudante sem nenhuma aula com open = 1 e abstract = 0, levanta erro aqui!
            '''
            cursor.execute(insert_into_classes_actual_str)
            #Insere na tabela 'students_classes_actual" os relacionamentos dos estudantes com as suas aulas atuais e ativas

            cursor.execute('select classes.id from classes join classes_courses on classes.id=classes_courses.id_class join ' \
            'courses on classes_courses.id_course=courses.id where classes.open=0 and courses.fk_institution=%s and courses.id=%s'
            'and abstract=1',
            [request.session.get("institution"),valid_course])
            # Busca os Ids das aulas que são da instituição do criador(courses_fk_institution),são do curso selecionado(courses.id)
            # e que são abstratas. O que é ser abstrata?
            '''
            Ser abstrata é servir de base para a criação de outras salas,ou seja,ser genérica. Desse modo, pode-se analisar se o
            estudante concluiu as X aulas necessárias para a conclusão do curso. Assim,quando o estudante ser aprovado em Y aula,
            a Y aula sumirá do student_classes_actual e sua equivalente abstrata também sumirá da student_classes_missing.

            '''

            classes_abstract=cursor.fetchall()
            if not classes_abstract:
                messages.error(request,"O curso não possui salas padrão!")
                dbf.safe_rollback(conn)
                return False
            insert_into_classes_missing_str="insert into students_classes_missing(id,id_class,id_student)values"
            for tupla in classes_abstract:
                if tupla == classes_abstract[-1]:
                    insert_into_classes_missing_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra});"
                else:
                    insert_into_classes_missing_str+=f"('{tupla[0]}-{valid_ra}',{tupla[0]},{valid_ra}),"

            cursor.execute(insert_into_classes_missing_str) #Fez a mesma operação já descrita acima
            conn.commit() # Faz o commit de todos os inserts --> Caso algo dê errado,dá rollback e anula os inserts
            return True # retorna verdadeiro caso o dê tudo certo
        else:
            messages.error(request,"Houve um erro no processamento dos dados!")
            return False
    except (errors.InvalidTextRepresentation,ValueError,errors.DeadlockDetected,errors.NotNullViolation,errors.NameTooLong,
            DatabaseError,errors.ForeignKeyViolation,errors.DatatypeMismatch,errors.UniqueViolation,TypeError):
        dbf.safe_rollback(conn)
        messages.error(request,"Algum dado inválido foi enviado!")
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
    except Exception :
        try:
            if conn:
             dbf.safe_rollback(conn)
        except Exception:
             pass
        messages.error(request,"Erro desconhecido!")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


'''
Cria as salas abstratas e as vinculam ao curso
Código relativamente complexo,será explicado ação por ação
'''
def principal_crs_creation_classes(request,name,acronym,e_mec,max_length)->bool:
    from psycopg2 import errors,errorcodes
    from django.contrib import messages
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor() #Inicializa a conexão
        if conn and cursor:
            # Insere (sem fzr commit) o curso anteriormente digitado pelo usuário (todas as variáveis foram previamente validadas)
            cursor.execute("insert into courses(name,acronym,e_mec,max_length,fk_institution)values(%s,%s,%s,%s,%s) returning id",
                           [name,acronym,e_mec,max_length,request.session.get("institution")])

            course_id:list=cursor.fetchone()[0] # Guarda o Id do novo curso (returning id)
            list_inputs_name:list=request.POST.getlist("class_id") # Pega os nomes digitados pelo usuário
            list_inputs_initial:list=request.POST.getlist("class_initial") # Pega as informações dos selects(inicial)
            list_values=[] #inicializa a lista de valores para o insert no banco

            for i in range(0,len(list_inputs_name)):
                if not f.validate_query_entries(list_inputs_name[i]): #Caso o usuário digite algo inválido,ele retorna falso
                    # e cancela a operação
                    messages.error(request,"Dado inválido enviado no formulário!")
                    conn.rollback()
                    return False
                else:

                    # list_values.append((nome,open,initial,abstract))
                    if list_inputs_initial[i] == "1":
                             list_values.append((list_inputs_name[i],0,1,1))
                    elif list_inputs_initial[i] == "0" :
                             list_values.append((list_inputs_name[i],0,0,1))

                    else:
                        #Caso o usuário digite algo inválido,ele retorna falso
                        # e cancela a operação
                        messages.error(request,"Dado inválido enviado no formulário!")
                        conn.rollback()
                        return False
            # Retorna uma lista de tuplas
            classes_id:list=execute_values(cursor,"insert into classes(name,open,initial,abstract)values %s returning id",list_values,fetch=True)
            classes_id_size=len(classes_id) #Pega o tamanho dessa lista de tuplas
            #Inicializa uma string para o insert
            string_insert_into_classes_courses="insert into classes_courses(id,id_class,id_course)values"
            # Percorre toda a lista de tuplas,acrescentando os dados de classes_id na string acima
            for i in range(0,classes_id_size):
                if i == classes_id_size-1:
                    string_insert_into_classes_courses+=(f"({classes_id[i][0]}-{course_id},{classes_id[i][0]},{course_id});")
                else:
                    string_insert_into_classes_courses+=(f"('{classes_id[i][0]}-{course_id}',{classes_id[i][0]},{course_id}),")
            cursor.execute(string_insert_into_classes_courses)
            conn.commit() # Commita e faz a inserção definitiva
            messages.success(request,"Curso criado com sucesso! Crie as salas para prosseguir!")
            return True # Retorna True se tudo der certo

        # Caso dê errado, tratamos os erros tentando fazer o rollback das operações feitas anteriormente para evitar erros
        # e inconsistências no banco de dados

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
Insere uma nova classe no banco de dados, também cria sua relação com o curso na tabela classes_courses
'''
def principal_cls_creation_operation_create_class(request,max_length,class_name,class_initial,academic_user_id,start_date,end_date):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if(conn and cursor):
            cursor.execute("insert into classes(name,max_students,start_date,end_date,open,fk_professor,initial,abstract)values" \
            "(%s,%s,%s,%s,%s,%s,%s,%s) returning id",
            [class_name,max_length,start_date,end_date,1,academic_user_id,class_initial,0])
            new_class_id=cursor.fetchone()[0]
            cursor.execute("insert into classes_courses(id,id_class,id_course)values(%s,%s,%s)",
                           [f"{new_class_id}-{request.session.get("actual_course")}",new_class_id,request.session.get("actual_course")])
            conn.commit()

            return True
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
Adiciona o relacionamento dos estudantes com uma sala, de maneira a respeitar o limite da sala
Além disso, cria o relacionamento dos estudantes com as tarefas já existentes na turma
'''
def principal_cls_edition_add_students(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            list_students_RA:list=request.POST.getlist("students_opt_del")
            if list_students_RA:
                actual_class_id=request.session.get("actual_class_id")
                listof_tuple_sql=[]
                listof_tuple_RA=[]
                for item in list_students_RA:
                   if f.validate_ids_entries(item):
                        listof_tuple_sql.append((f"{actual_class_id}-{item}",actual_class_id,item,0,0))
                        listof_tuple_RA.append((item,))
                   else:
                       messages.error(request,"Alteração indevida no formulário")
                       
                       return False
                cursor.execute('select students."RA" from students where students.fk_course = any(select courses.id from' \
                ' courses join classes_courses on courses.id=classes_courses.id_course join classes ' \
                'on classes_courses.id_class=classes.id where classes.id=%s ) and students.fk_institution=%s',
                [actual_class_id,request.session.get("institution")])
                students_query=cursor.fetchall()

                cursor.execute('select count(*) from students_classes_actual where students_classes_actual.id_class=%s',
                               [actual_class_id])
                sizeof_class=cursor.fetchone()

                if sizeof_class:
                    sizeof_class=sizeof_class[0]
                else:
                    messages.error(request,"Houve um erro na consulta ao banco de dados!")
                    
                    return False
                cursor.execute("select max_students from classes where id =%s",[actual_class_id])
                max_size=cursor.fetchone()
                if max_size:
                    max_size=max_size[0]
                else:
                   
                    messages.error(request,"Houve um erro na consulta ao banco de dados!")
                    return False
                if len(listof_tuple_sql)>(max_size-sizeof_class):

                    messages.error(request,"Você tentou inserir mais itens do que o permitido!")
                    return False
                else:
                    if(set(listof_tuple_RA).issubset(students_query)):
                        execute_values(cursor,"insert into students_classes_actual(id,id_class,id_student,absence,attendance) values %s",
                        listof_tuple_sql)

                        cursor.execute("select assignments.id from assignments where assignments.fk_class=%s",
                        [actual_class_id])

                        listof_tuple_assignment=cursor.fetchall()
                        if listof_tuple_assignment:

                            listof_tuple_assignments_students=[]

                            for i in range(0,len(listof_tuple_RA)):

                                for j in range(0,len(listof_tuple_assignment)):

                                    listof_tuple_assignments_students.append((list_students_RA[i],
                                                                              listof_tuple_assignment[j][0]))
                        
                            execute_values(cursor,"insert into assignments_students(fk_student,fk_assignment) values %s",
                                           listof_tuple_assignments_students)
                            
                        else:
                            pass
                        conn.commit()
                        return True
                    else:
                        dbf.safe_rollback(conn)
                        messages.error(request,"Alteração indevida nos campos!")
                        return False
            else:
               
                messages.error(request,"Você não inseriu nenhum campo válido!")
                return False


        else:
            messages.error(request,"Erro com a conexão ao banco de dados!")
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

def professor_add_assignment_operation(request):
    conn,cursor=None,None
    try:
        conn,cursor=f.connection_cursor()
        if conn and cursor:
            is_valid_name=f.regex_list_to_string(
            f.validate_query_entries(request.POST.get("name")))

            is_valid_desc=f.regex_list_to_string(
            f.validate_texts(request.POST.get("desc")))

            is_valid_deadline=f.validate_date(request.POST.get("deadline"))

            is_valid_weight=f.validate_grades_and_weights(request.POST.get("weight"))

            is_valid_max_grade=f.validate_grades_and_weights(request.POST.get("weight"))

            if is_valid_name and is_valid_desc and is_valid_deadline and is_valid_weight and is_valid_max_grade:
            
                valid_weight=abs(is_valid_weight)
                valid_max_grade=abs(is_valid_max_grade)
                # Puxando dados dos alunos da sala
                students_query=read.professor_add_assignment_get_all_students_by_class(request,conn,cursor)
                if students_query:
                    cursor.execute('insert into assignments(name,fk_class,deadline,"desc",max_grade,weight)'
                    'values(%s,%s,%s,%s,%s,%s) returning id',[is_valid_name,request.session.get("actual_class_id"),
                   is_valid_deadline,is_valid_desc,valid_max_grade,valid_weight])
                    new_assignment_id_tuple=cursor.fetchone()
                    
                    if new_assignment_id_tuple:
                        list_insert_values=[]
                        for register in students_query:
                            list_insert_values.append((register[0],new_assignment_id_tuple[0]))
                        execute_values(cursor,"insert into assignments_students(fk_student,fk_assignment) values %s"
                        ,list_insert_values)
                        conn.commit()
                        messages.success(request,"Adição feita com sucesso!")
                        return True
                    else:
                        dbf.safe_rollback(conn)
                        messages.error(request,"Houve um erro com a criação da sua tarefa!")
                        return False
                else:
                    dbf.safe_rollback(conn)
                    messages.error(request,"Não há alunos nessa sala,consulte o diretor responsável!")
                    return False
            else:
                dbf.safe_rollback(conn)
                messages.error(request,"Alguma informação inválida foi enviada!")
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