from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Version(models.Model):
    version_name = models.CharField(max_length=100)

    def __str__(self):
        return self.version_name

class StmBuild(models.Model):
    build_number = models.CharField(max_length=100)
    version = models.ForeignKey(Version , related_name='build' , on_delete=models.CASCADE)
    total_testCase= models.IntegerField()
    passed_testCase= models.IntegerField()
    failed_testCase = models.IntegerField()
    pass_percentage = models.IntegerField()

    def __str__(self):
        return self.build_number 
    
class Script(models.Model):
    build = models.ForeignKey(StmBuild , on_delete=models.CASCADE , related_name='testCases')
    name = models.CharField(max_length=100)
    total_testCase = models.IntegerField()
    passed_testCase = models.IntegerField()
    failed_testCase = models.IntegerField()

    def __str__(self):
        return self.name

class ScriptTestInfo(models.Model):
    script = models.ForeignKey(Script , on_delete=models.CASCADE , related_name='failedScripts')
    status = models.CharField(max_length=100)
    message = models.TextField(max_length=100)
    main =   ArrayField(base_field=models.TextField(),size=2)

    def __str__(self):
        return self.script.build.build_number + "_" + self.script.name + "_" + self.status
    
    
    
