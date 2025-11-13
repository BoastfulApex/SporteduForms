from django.contrib import admin
from .models import FormCategory, Question, Answer, UserAnswer


admin.site.register(UserAnswer)
admin.site.register(Answer)
# Register your models here.
