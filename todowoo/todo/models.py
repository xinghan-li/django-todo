from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    title = models.CharField(max_length=100)
    memo = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True) # timestamp
    datecompleted = models.DateTimeField(null=True, blank=True) # datetime format use null
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # display the title for each object
    def __str__(self):
        return self.title