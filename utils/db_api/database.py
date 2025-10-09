from datetime import datetime, timedelta
from asgiref.sync import sync_to_async
from django.db.models import F
from apps.main.models import *
from apps.forms.models import *


# ======== USER FUNKSIYALARI =========
@sync_to_async
def check_user(user_id):
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    return user.finish if user else False


@sync_to_async
def add_user(user_id, username, first_name, lang):
    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y %B")
    user, created = TelegramUser.objects.get_or_create(telegram_id=user_id)
    user.lang = lang
    user.username = username
    user.first_name = first_name
    user.study_period = formatted_date
    user.save()
    return user


@sync_to_async
def get_user(user_id):
    return TelegramUser.objects.filter(telegram_id=user_id).first()


@sync_to_async
def get_lang(user_id):
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    return user.lang if user else None


# ======== FILIAL / YO‘NALISH / GURUH TANLASH FUNKSIYALARI =========
@sync_to_async
def get_all_filials():
    """Barcha filiallar ro‘yxatini qaytaradi."""
    return list(Filial.objects.all())


@sync_to_async
def get_study_fields_by_filial(filial_id):
    """Filial bo‘yicha yo‘nalishlarni qaytaradi."""
    # Agar StudyField Filial bilan bog‘liq bo‘lsa — kerakli filterni qo‘ying.
    return list(StudyField.objects.all())


@sync_to_async
def get_current_month_groups(filial_id=None, study_field_id=None):
    """Hozirgi oy uchun guruhlarni qaytaradi."""
    now = datetime.now()
    groups = Group.objects.filter(
        year__year=now.year,
        month__number=now.month
    )
    if filial_id:
        groups = groups.filter(filial_id=filial_id)
    if study_field_id:
        groups = groups.filter(study_field_id=study_field_id)
    return list(groups)


@sync_to_async
def set_filial(filial_name, user_id):
    """Foydalanuvchiga filialni biriktiradi."""
    filial = Filial.objects.filter(name_uz=filial_name).first() or \
             Filial.objects.filter(name_ru=filial_name).first()
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user and filial:
        user.filial = filial
        user.save()


@sync_to_async
def set_study_field(name, user_id):
    """Foydalanuvchiga tanlangan yo‘nalishni biriktiradi."""
    field = StudyField.objects.filter(study_field_uz=name).first() or \
            StudyField.objects.filter(study_field_ru=name).first()
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user and field:
        user.field_of_study = field
        user.save()
    return field


@sync_to_async
def set_group(group_name, user_id):
    """Foydalanuvchiga tanlangan guruhni biriktiradi."""
    group = Group.objects.filter(name_uz=group_name).first() or \
            Group.objects.filter(name_ru=group_name).first()
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user and group:
        user.group = group
        user.save()


# ======== SAVOL / JAVOB FUNKSIYALARI =========
@sync_to_async
def get_question(index):
    questions = Question.objects.filter(active=True).order_by('id')
    return questions[int(index)] if 0 <= int(index) < len(questions) else None


@sync_to_async
def get_multi_or_not(index):
    question = get_question(index)
    return question.multi_answer if question else False


@sync_to_async
def get_answers(question_id):
    return list(Answer.objects.filter(question_id=question_id))


@sync_to_async
def update_answer(answer_id, user_id, question_id):
    try:
        answer = Answer.objects.get(id=answer_id)
        answer.answers_count = F('answers_count') + 1
        answer.save(update_fields=['answers_count'])
        user = TelegramUser.objects.get(telegram_id=user_id)
        question = Question.objects.get(id=question_id)

        user_answer, _ = UserAnswer.objects.get_or_create(user=user, question=question)
        if answer in user_answer.answer.all():
            user_answer.answer.remove(answer)
        else:
            user_answer.answer.add(answer)
    except Exception as exx:
        print("update_answer xatosi:", exx)


@sync_to_async
def finish_user(user_id):
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user:
        user.finish = True
        user.save()
    return user


# ======== LOCATION / COMMENT FUNKSIYALARI =========
@sync_to_async
def set_location(loc_name, user_id):
    location = Location.objects.filter(location_uz=loc_name).first() or \
               Location.objects.filter(location_ru=loc_name).first()
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user and location:
        user.location = location
        user.save()


@sync_to_async
def set_comment_1(user_id, comment):
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user:
        user.comment_1 = comment
        user.save()


@sync_to_async
def set_comment_2(user_id, comment):
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    if user:
        user.comment_2 = comment
        user.save()


@sync_to_async
def get_filial_from_db(user_id: int):
    """
    Foydalanuvchiga tegishli filial(lar)ni qaytaradi.
    Agar foydalanuvchining filial bog‘lanmagan bo‘lsa, bo‘sh ro‘yxat qaytaradi.
    """
    try:
        user = TelegramUser.objects.filter(telegram_id=user_id).select_related("filial").first()
        if user and user.filial:
            return user.filial
        return []
    except Exception as ex:
        print(f"❌ Filialni olishda xatolik: {ex}")
        return []

    
@sync_to_async
def create_student(user_id, group_id):
    """Foydalanuvchini Student sifatida yaratadi."""
    try:
        user = TelegramUser.objects.filter(telegram_id=user_id).first()
        group = Group.objects.filter(id=group_id).first()
        if user and group:
            student, created = Student.objects.get_or_create(telegram_user=user, group=group)
            return student
        return None
    except Exception as ex:
        print(f"❌ Student yaratishda xatolik: {ex}")
        return None
    

@sync_to_async
def get_active_modules(group_id):
    """Berilgan guruh uchun faqat active modullarni qaytaradi"""
    
    return list(
        GroupModuleTeacher.objects.select_related("study_module")
        .filter(group_id=group_id, active=True)
    )
    

@sync_to_async
def get_active_modules(group_id):
    return list(
        GroupModuleTeacher.objects.filter(group_id=group_id, active=True)
        .select_related("study_module")
    )

@sync_to_async
def get_form_category():
    return FormCategory.objects.filter(active=True).first()


@sync_to_async
def get_questions(category_id):
    return list(
        Question.objects.filter(form_category_id=category_id, active=True).order_by("id")
    )
    

@sync_to_async
def get_user_study_field(user_id):
    user = TelegramUser.objects.filter(telegram_id=user_id).first()
    return user.field_of_study if user else None