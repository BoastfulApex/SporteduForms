from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone


class Year(models.Model):
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class Month(models.Model):
    month = models.IntegerField()
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="months")
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"{self.month}/{self.year.year}"


INSTITUT, NUKUS, SAMARQAND, FERGANA = (
    "Institut",
    "Nukus filiali",
    "Samarqand filiali",
    "Farg'ona filiali",
)


class Filial(models.Model):
    name_uz = models.CharField(max_length=1000, null=True, blank=True)
    name_ru = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name_uz or self.name_ru


class Location(models.Model):
    location_uz = models.CharField(max_length=100)
    location_ru = models.CharField(max_length=100)

    def __str__(self):
        return self.location_uz


class StudyField(models.Model):
    study_field_uz = models.CharField(max_length=1000, null=True, blank=True)
    study_field_ru = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.study_field_uz or self.study_field_ru


class Group(models.Model):
    name_uz = models.CharField(max_length=1000, null=True, blank=True)
    name_ru = models.CharField(max_length=1000, null=True, blank=True)
    study_field = models.ForeignKey(StudyField, on_delete=models.CASCADE, related_name="groups")
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="groups")
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="groups")
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return self.name_uz or self.name_ru


class TelegramUser(models.Model):
    FILIALS = (
        (INSTITUT, INSTITUT),
        (NUKUS, NUKUS),
        (SAMARQAND, SAMARQAND),
        (FERGANA, FERGANA)
    )

    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=1000, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)

    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="telegram_users", null=True, blank=True)
    age = models.IntegerField(null=True)
    sport_type = models.CharField(max_length=100, null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    languages = models.CharField(max_length=100, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name="telegram_users")
    lang = models.CharField(max_length=10, null=True)
    study_period = models.CharField(max_length=50, null=True)
    field_of_study = models.ForeignKey(StudyField, null=True, blank=True, on_delete=models.SET_NULL, related_name="telegram_users")
    finish = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.telegram_id}"


class Student(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="students")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="students")
    created_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.telegram_user} - {self.group}'


class StudyModule(models.Model):
    name = models.CharField(max_length=1000, null=True, blank=True)
    study_field = models.ForeignKey(StudyField, on_delete=models.CASCADE, related_name="modules")
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="modules")

    def __str__(self):
        return self.name


class Cafedra(models.Model):
    name_uz = models.CharField(max_length=1000, null=True, blank=True)
    name_ru = models.CharField(max_length=1000, null=True, blank=True)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="cafedras")

    def __str__(self):
        return self.name_uz or self.name_ru


class Teacher(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="teachers")
    name = models.CharField(max_length=1000, null=True, blank=True)
    cafedra = models.ForeignKey(Cafedra, null=True, blank=True, on_delete=models.SET_NULL, related_name="teachers")

    def __str__(self):
        return self.name


class GroupModuleTeacher(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="teacher_modules", null=True)
    study_module = models.ForeignKey(StudyModule, on_delete=models.CASCADE, related_name="teacher_modules")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="teacher_modules")
    active = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f'{self.teacher} - {self.study_module}'

    class Meta:
        unique_together = ('teacher', 'study_module', 'group')


  