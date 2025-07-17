from django.db import models
from django.utils import timezone

# Create your models here.
class register(models.Model):                  #register
    username=models.CharField(max_length=20)     
    email = models.EmailField(max_length=50,unique=True)
    password= models.CharField(max_length=50)
    password1= models.CharField(max_length=50)
    
    def __str__(self):
        return self.username 

class expense_store(models.Model):
   user = models.ForeignKey(register,to_field='email',on_delete=models.CASCADE,related_name='expenses')
   date = models.DateField()
   amount = models.FloatField()
   mode = models.CharField(max_length=20)
   category = models.CharField(max_length=50)
    
def current_month():
    return timezone.now().month

def current_year():
    return timezone.now().year

class MonthlyLimit(models.Model):
    user = models.ForeignKey(register, on_delete=models.CASCADE)
    amount = models.FloatField()
    month = models.IntegerField(default=current_month)
    year = models.IntegerField(default=current_year)

    class Meta:
        unique_together = ('user', 'month', 'year')

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}: {self.amount}"
