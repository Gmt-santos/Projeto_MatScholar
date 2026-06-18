from django.db import models

# Create your models here.
class institution(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    acronym=models.CharField(max_length=255)
    cnpj=models.CharField(max_length=255)
    class Meta:
        db_table='institution'

class permissions(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    nickname=models.CharField(max_length=255)
    class Meta:
        db_table='permissions'


class courses(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    acronym=models.CharField(max_length=255,null=True)
    e_mec=models.CharField(max_length=255)
    max_length=models.IntegerField()
    fk_institution=models.ForeignKey(institution,on_delete=models.CASCADE,db_column="fk_institution",null=True)
    class Meta:
        db_table='courses'

class academic_users(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    role=models.CharField(max_length=255)
    fk_institution=models.ForeignKey(institution,on_delete=models.CASCADE,db_column="fk_institution")
    email=models.CharField(max_length=255,null=True)
    password=models.CharField(max_length=255,null=True)
    class Meta:
        db_table='academic_users'
    
class students(models.Model):
    RA=models.CharField(max_length=255,primary_key=True)
    name=models.CharField(max_length=255)
    year_of_entry=models.IntegerField()
    fk_course=models.ForeignKey(courses,on_delete=models.CASCADE,db_column="fk_course")
    password=models.CharField(max_length=255)
    fk_institution=models.ForeignKey(institution,on_delete=models.CASCADE,db_column="fk_institution",null=True)
    class Meta:
        db_table='students'


class academic_users_permissions(models.Model):
    id=models.CharField(max_length=255,primary_key=True)
    id_user=models.ForeignKey(academic_users,on_delete=models.CASCADE,db_column="id_user")
    id_nickname=models.ForeignKey(permissions,on_delete=models.CASCADE,db_column="id_nickname")
    class Meta:
        db_table='academic_users_permissions'

class classes(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    max_students=models.IntegerField(null=True)
    start_date=models.DateField(null=True)
    end_date=models.DateField(null=True)
    open=models.IntegerField()
    fk_professor=models.ForeignKey(academic_users,on_delete=models.CASCADE,db_column="fk_professor",null=True)
    initial=models.IntegerField(default=1)
    abstract=models.IntegerField(default=0)
    class Meta:
        db_table='classes'

class classes_courses(models.Model):
    id=models.CharField(max_length=255,primary_key=True)
    id_class=models.ForeignKey(classes,on_delete=models.CASCADE,db_column="id_class")
    id_course=models.ForeignKey(courses,on_delete=models.CASCADE,db_column="id_course")
    class Meta:
        db_table='classes_courses'

class students_classes_actual(models.Model):
    id=models.CharField(max_length=255,primary_key=True)
    id_class=models.ForeignKey(classes,on_delete=models.CASCADE,db_column="id_class")
    id_student=models.ForeignKey(students,on_delete=models.CASCADE,db_column="id_student")
    class Meta:
        db_table='students_classes_actual'

class students_classes_missing(models.Model):
    id=models.CharField(max_length=255,primary_key=True)
    id_class=models.ForeignKey(classes,on_delete=models.CASCADE,db_column="id_class")
    id_student=models.ForeignKey(students,on_delete=models.CASCADE,db_column="id_student")
    class Meta:
        db_table='students_classes_missing'



class assignments(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=255)
    fk_id_student=models.ForeignKey(students,on_delete=models.CASCADE,db_column="fk_id_student")
    fk_class=models.ForeignKey(classes,on_delete=models.CASCADE,db_column="fk_class")
    grade=models.DecimalField(max_digits=10,decimal_places=2)
    class Meta:
        db_table='assignments'



class final_grades(models.Model):
    id=models.CharField(max_length=255,primary_key=True)
    
    id_student=models.ForeignKey(students,on_delete=models.CASCADE,db_column="id_student")
    id_class=models.ForeignKey(classes,on_delete=models.CASCADE,db_column="id_class")
    final_grade=models.DecimalField(max_digits=10,decimal_places=2)
    class Meta:
        db_table='final_grades'