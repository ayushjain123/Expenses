from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# Create your models here.
class UserIncome(models.Model):
    amount= models.IntegerField()
    date= models.DateTimeField(default=now, blank=True, null=True)
    description= models.TextField()
    owner= models.ForeignKey(to=User, on_delete=models.CASCADE)
    source= models.CharField(max_length=255)


    def __str__(self):
        return self.source

    class Meta:
        ordering: ['-date']

class Source(models.Model):
    source=models.CharField(max_length=255)

    def __str__(self):
        return self.source
