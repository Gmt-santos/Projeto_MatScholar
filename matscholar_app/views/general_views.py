from django.shortcuts import render,redirect

# Create your views here.
def index(request):
    '''
    Serve para caso o usuário(academic_user) não esteja mais interagindo com a sala ou o curso
    '''
    '''
    Serve para caso o usuário não esteja mais interagindo com a sala ou o curso
    '''
    if request.session.get("actual_class"):
        del request.session["actual_class"]
    if request.session.get("actual_class_initial"):
        del request.session["actual_class_initial"]
    if request.session.get("actual_course"):
        del request.session["actual_course"]
    if request.session.get("actual_class_id"):
        del request.session["actual_class_id"]
    if request.session.get("actual_student_RA"):
        del request.session["actual_student_RA"]

    return render(request,'index.html')
