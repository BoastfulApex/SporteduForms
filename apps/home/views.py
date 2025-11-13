from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, render,get_object_or_404
from apps.authentication.models import *
from apps.main.forms import *
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib import messages
from apps.forms.forms import *
import openpyxl
from django.urls import reverse
from django.db.models import Sum, Max, F



def index(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    template = 'home/index.html'

    context = {
        'segment': 'dashboard',
    
    }
    html_template = loader.get_template(template)
    return HttpResponse(html_template.render(context, request))


def groups(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    template = 'home/user/groups/groups.html'
    groups = Group.objects.all()
    paginator = Paginator(groups, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    tashkent_time = timezone.localtime(timezone.now())
    context = {
        'segment': 'groups',
        'page_obj': page_obj,
    }
    html_template = loader.get_template(template)
    return HttpResponse(html_template.render(context, request))


def group_create(request):
    if request.method == "POST":
        print(request.POST)
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("groups")
        else:
            print(form.errors)
    else:
        form = GroupForm()
    return render(request, "home/user/groups/groups_create.html", {"form": form, 'segment': 'groups'})


def load_months(request):
    year_id = request.GET.get("year_id")
    months = Month.objects.filter(year_id=year_id).order_by("month")
    return JsonResponse(list(months.values("id", "name")), safe=False)

class GroupDelete(DeleteView):
    model = Group
    template_name = 'home/user/groups/group_confirm_delete.html'
    success_url = reverse_lazy('groups')
    

def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("teachers")
    else:
        form = TeacherForm()
    return render(request, "home/user/teachers/teacher_create.html", {"form": form, 'segment': 'teachers'})


def teachers(request):
    teachers = Teacher.objects.select_related("filial").all()
    template = 'home/user/teachers/teachers.html'
    paginator = Paginator(teachers, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    tashkent_time = timezone.localtime(timezone.now())
    context = {
        'segment': 'teachers',
        'page_obj': page_obj,
    }
    html_template = loader.get_template(template)
    return HttpResponse(html_template.render(context, request))

class TeacherDelete(DeleteView):
    model = Teacher
    template_name = 'home/user/teachers/teacher_confirm_delete.html'
    success_url = reverse_lazy('teachers')
    

def study_module_list(request):

    # Filial bo‘yicha modullar
    modules = StudyModule.objects.all()

    # Qidiruv
    search_query = request.GET.get("q", "")
    if search_query:
        modules = modules.filter(
            Q(name__icontains=search_query) |
            Q(study_field__study_field_uz__icontains=search_query) |
            Q(study_field__study_field_ru__icontains=search_query)
        )

    # Paginator
    paginator = Paginator(modules, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Toshkent vaqti
    tashkent_time = timezone.localtime(timezone.now())

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "tashkent_time": tashkent_time,
        'segment': 'study_modules',
    }
    return render(request, "home/user/modules/module_list.html", context)


def study_module_create(request):
    if request.method == "POST":
        form = StudyModuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("study_module_list")  # Ro‘yxatga qaytadi
    else:
        form = StudyModuleForm()

    return render(request, "home/user/modules/module_create.html", {"form": form, 'segment': 'study_modules'})


class StudyModuleDelete(DeleteView):
    model = StudyModule
    template_name = 'home/user/modules/study_module_confirm_delete.html'
    success_url = reverse_lazy('study_module_list')
    

def study_module_upload(request):
    if request.method == "POST":
        form = StudyModuleUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES["file"])
            study_field = form.cleaned_data["study_field"]
            filial = form.cleaned_data["filial"]
            file = request.FILES["file"]

            try:
                workbook = openpyxl.load_workbook(file)
                sheet = workbook.active

                count = 0
                for row in sheet.iter_rows(min_row=2, values_only=True):  # 1-qatorda sarlavha
                    name = row[0]  # 1-ustunda modul nomi
                    if name:
                        StudyModule.objects.create(
                            name=name,
                            filial=filial,
                            study_field=study_field
                        )
                        count += 1

                messages.success(request, f"{count} ta modul muvaffaqiyatli qo‘shildi!")
                return redirect("study_module_list")

            except Exception as e:
                print(str(e))
                messages.error(request, f"Xato: {str(e)}")

    else:
        form = StudyModuleUploadForm()

    return render(request, "home/user/modules/module_upload.html", {"form": form, 'segment': 'study_modules'})


def group_modules(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Guruhga bog'langan modullarni olish
    modules = GroupModuleTeacher.objects.filter(group=group).select_related("teacher", "study_module")

    # Agar hech qanday GroupModuleTeacher yo'q bo'lsa
    if not modules.exists():
        # Guruhning study_field modullarini olish
        study_modules = StudyModule.objects.filter(study_field=group.study_field)

        new_links = []
        for sm in study_modules:
            gmt = GroupModuleTeacher.objects.create(
                teacher=None,  # hozircha teacher tanlanmagan
                study_module=sm,
                group=group
            )
            new_links.append(gmt)

        modules = new_links  # yangi yaratilganlarni ishlatamiz

    return render(request, "home/user/groups/group_modules.html", {
        "group": group,
        "modules": modules,
        'segment': 'groups',
    })
    
    

def assign_teacher(request, group_module_id):
    gmt = get_object_or_404(GroupModuleTeacher, id=group_module_id)

    if request.method == "POST":
        form = AssignTeacherForm(request.POST, instance=gmt)
        if form.is_valid():
            form.save()
            return redirect("group_modules", group_id=gmt.group.id)
    else:
        form = AssignTeacherForm(instance=gmt)

    return render(request, "home/user/groups/assign_teacher.html", {
        "form": form,
        "gmt": gmt,
        'segment': 'groups',
    })
    

def toggle_group_module_teacher_active(request, pk):
    instance = get_object_or_404(GroupModuleTeacher, pk=pk)
    if request.method == "POST":
        form = GroupModuleTeacherActiveForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("group_modules", group_id=instance.group.id)
    else:
        form = GroupModuleTeacherActiveForm(instance=instance)
    return render(request, "home/user/groups/edit_active.html", {"form": form, "instance": instance, 'segment': 'groups'})



def form_category_list(request):
    search_query = request.GET.get('q', '')
    form_categories = FormCategory.objects.all()

    if search_query:
        form_categories = form_categories.filter(
            Q(name_uz__icontains=search_query) | Q(name_ru__icontains=search_query)
        )

    paginator = Paginator(form_categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'home/user/formcategory/form_category_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'segment': 'form_categories'
    })


def form_category_create(request):
    if request.method == 'POST':
        form = FormCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('form_category_list')
    else:
        form = FormCategoryForm()
    return render(request, 'home/user/formcategory/form_category_form.html', {'form': form, 'title': 'Yangi kategoriya qo‘shish', 'segment': 'form_categories'})


def form_category_update(request, pk):
    category = get_object_or_404(FormCategory, pk=pk)
    if request.method == 'POST':
        form = FormCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('form_category_list')
    else:
        form = FormCategoryForm(instance=category)
    return render(request, 'home/user/formcategory/form_category_form.html', {'form': form, 'title': 'Kategoriyani tahrirlash', 'segment': 'form_categories'})



def form_category_delete(request, pk):
    category = get_object_or_404(FormCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('form_category_list')
    return render(request, 'home/user/formcategory/form_category_confirm_delete.html', {'category': category, 'segment': 'form_categories'})



def question_list(request):
    search_query = request.GET.get('q', '')
    questions = Question.objects.all().order_by('-id')

    if search_query:
        questions = questions.filter(
            Q(question_uz__icontains=search_query) |
            Q(question_ru__icontains=search_query)
        )

    paginator = Paginator(questions, 20)  # Har sahifada 20 ta savol
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'segment': 'questions'
    }
    return render(request, "home/user/question/question_list.html", context)

def question_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("question_list")
    else:
        form = QuestionForm()
    return render(request, "home/user/question/question_create.html", {"form": form, 'segment': 'questions'})


def question_update(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect("question_list")
    else:
        form = QuestionForm(instance=question)
    return render(request, "home/user/question/question_edit.html", {"form": form, "question": question, 'segment': 'questions'})


def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        question.delete()
        return redirect("question_list")
    return render(request, "home/user/question/question_delete.html", {"object": question, 'segment': 'questions'})


def answer_list(request):
    search_query = request.GET.get('q', '')
    answers = Answer.objects.all()

    if search_query:
        answers = answers.filter(
            Q(answer_uz__icontains=search_query) |
            Q(question__question_uz__icontains=search_query)
        )

    paginator = Paginator(answers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "home/user/answers/answers_list.html", {
        "page_obj": page_obj,
        "search_query": search_query,
        "segment": "answers"
    })


def answer_create(request):
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("answer_list")
    else:
        form = AnswerForm()
    return render(request, "home/user/answers/answer_form.html", {"form": form, "segment": "answers", "title": "Yangi javob qo'shish"})


def answer_edit(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect("answer_list")
    else:
        form = AnswerForm(instance=answer)
    return render(request, "home/user/answers/answer_form.html", {"form": form,"segment": "answers", "title": "Javobni tahrirlash"})


def answer_delete(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.method == "POST":
        answer.delete()
        return redirect("answer_list")
    return render(request, "home/user/answers/answer_delete.html", {"answer": answer, "segment": "answers"})


# def add_answer_view(request):
#     """
#     Bitta question tanlanadi va bir nechta javoblar formset orqali kiritiladi.
#     """
#     title = "Javoblar qo‘shish"
#     question_form = QuestionSelectForm(request.POST or None)
#     formset = AddAnswerFormSet(request.POST or None, queryset=Answer.objects.none())

#     if request.method == "POST":
#         if question_form.is_valid() and formset.is_valid():
#             question = question_form.cleaned_data['question']

#             for form in formset:
#                 if form.cleaned_data and not form.cleaned_data.get('DELETE'):
#                     answer = form.save(commit=False)
#                     answer.question = question
#                     answer.save()

#             return redirect('answer_list')
#         else:
#             print(question_form.errors, formset.errors)
#     context = {
#         "title": title,
#         "form": question_form,
#         "formset": formset,
#     }
#     return render(request, 'home/user/answers/answer_dynamic_form.html', context)


def add_answer_view(request):
    title = "Javoblar qo‘shish"
    question_form = QuestionSelectForm(request.POST or None)
    formset = AddAnswerFormSet(request.POST or None, queryset=Answer.objects.none())

    if request.method == "POST":
        if question_form.is_valid() and formset.is_valid():
            question = question_form.cleaned_data['question']
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    answer = form.save(commit=False)
                    answer.question = question
                    answer.save()

            # 🔁 AJAX yuborilgan bo‘lsa, JSON qaytaramiz
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "redirect_url": reverse("answer_list")
                })
            else:
                return redirect('answer_list')

        # Agar xato bo‘lsa
        elif request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": False,
                "errors": {
                    "question_errors": question_form.errors,
                    "formset_errors": formset.errors
                }
            }, status=400)

    context = {
        "title": title,
        "form": question_form,
        "formset": formset,
        "segment": "answers"
    }
    return render(request, "home/user/answers/answer_dynamic_form.html", context)


def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            filial = form.cleaned_data['filial']
            # bu yerda siz ma’lumotni saqlashingiz yoki qayta ishlashingiz mumkin
            selected_month = form.cleaned_data['month']

            teachers = Teacher.objects.filter(
                teacher_modules__group__month_id=month
            ).distinct()   

            report_data = []

            for teacher in teachers:
                teacher_modules = GroupModuleTeacher.objects.filter(teacher=teacher)
                teacher_total_score = 0
                teacher_max_score = 0
                                    

                for module in teacher_modules:
                    # Shu modulga berilgan barcha javoblar
                    user_answers = UserAnswer.objects.filter(module=module).all()
                    for ua in user_answers:  # user_answers = UserAnswer queryset
                        for ans in ua.answer.all():
                            teacher_total_score += ans.score
                            teacher_max_score += Answer.objects.filter(question=ua.question).aggregate(max_score=Max('score'))['max_score'] or 0
                percent = round((teacher_total_score / teacher_max_score * 100), 2) if teacher_max_score else 0
                report_data.append({
                    'teacher': teacher.name,
                    'total_score': teacher_total_score,
                    'max_score': teacher_max_score,
                    'percent': percent,
                })
            # Foiz bo‘yicha tartiblash
            report_data.sort(key=lambda x: x['percent'], reverse=True)
        return render(request, 'home/reports/teacher_report.html', {
            'form': form,
            'report_data': report_data,
            'segment': 'reports'
        })
    else:
        form = ScheduleForm()
    return render(request, 'home/reports/select_date.html', {'form': form, 'segment': 'reports'})


def ajax_load_months(request):
    year_id = request.GET.get('year_id')
    months = Month.objects.filter(year_id=year_id).values('id', 'name')
    return JsonResponse(list(months), safe=False)