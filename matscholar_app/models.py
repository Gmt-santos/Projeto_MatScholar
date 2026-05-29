from django.db import models

# Create your models here.
class institution(models.Model):
    id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=255)
    acronym=models.CharField(max_length=255)
    cnpj=models.CharField(max_length=255)

class permissions(models.Model):
    id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=255)
    nickname=models.CharField(max_length=255)

class courses(models.Model):
    id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=255)
    e_mec=models.CharField(max_length=255)
    max_length=models.IntegerField()