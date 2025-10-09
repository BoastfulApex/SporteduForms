from django.db import models
from apps.main.models import Filial, Student, GroupModuleTeacher


class FormCategory(models.Model):
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    active = models.BooleanField(default=False, null=True)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="form_categories")
    for_rating = models.BooleanField(default=False, null=True)
    active = models.BooleanField(default=True, null=True)    
    def __str__(self):
        return self.name_uz

    def save(self, *args, **kwargs):
        # Agar yangi obyekt for_rating=True bo‘lsa,
        # boshqa barcha obyektlardagi for_rating=False qilib qo‘yiladi
        if self.for_rating:
            FormCategory.objects.exclude(pk=self.pk).update(for_rating=False)
            FormCategory.objects.exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)


class Question(models.Model):
    form_category = models.ForeignKey(FormCategory, on_delete=models.CASCADE, related_name="questions", null=True)
    question_uz = models.TextField(max_length=3000)
    question_ru = models.TextField(max_length=3000)
    multi_answer = models.BooleanField(default=False)
    text_answer = models.BooleanField(default=False)
    active = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.question_uz


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_uz = models.CharField(max_length=2000)
    answer_ru = models.CharField(max_length=2000)
    answers_count = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.answer_uz} - {self.question.question_uz}'
      

class UserAnswer(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    module = models.ForeignKey(GroupModuleTeacher, on_delete=models.CASCADE, null=True)
    answer = models.ManyToManyField(Answer, null=True)
    text_answer = models.TextField(max_length=3000, null=True, blank=True)


    def __str__(self):
        return f'{self.user.telegram_id} - {self.question.question_uz}'


