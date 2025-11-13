from django.urls import path
from apps.home import views

urlpatterns = [

    path('', views.index, name='home'),
    path('groups/', views.groups, name='groups'),
    path("groups/create/", views.group_create, name="group_create"),
    path("ajax/load-months/", views.load_months, name="ajax_load_months"),
    path("groups/delete/<int:pk>/", views.GroupDelete.as_view(), name="group_delete"),
    path('teachers/', views.teachers, name='teachers'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path("teachers/delete/<int:pk>/", views.TeacherDelete.as_view(), name="teacher_delete"),
    path("modules/", views.study_module_list, name="study_module_list"),
    path("modules/create/", views.study_module_create, name="study_module_create"),
    path("modules/delete/<int:pk>/", views.StudyModuleDelete.as_view(), name="module_delete"),
    path("modules/upload/", views.study_module_upload, name="study_module_upload"),
    path("groups/<int:group_id>/modules/", views.group_modules, name="group_modules"),
    path("groups/<int:group_module_id>/assign-teacher/", views.assign_teacher, name="assign_teacher"),
    path('group-module/<int:pk>/toggle/', views.toggle_group_module_teacher_active, name='group_module_active'),

    path('form-categories/', views.form_category_list, name='form_category_list'),
    path('form-categories/create/', views.form_category_create, name='form_category_create'),
    path('form-categories/<int:pk>/edit/', views.form_category_update, name='form_category_update'),
    path('form-categories/<int:pk>/delete/', views.form_category_delete, name='form_category_delete'),
    path("questions/", views.question_list, name="question_list"),
    path("questions/create/", views.question_create, name="question_create"),
    path("questions/<int:pk>/edit/", views.question_update, name="question_edit"),
    path("questions/<int:pk>/delete/", views.question_delete, name="question_delete"),
    path("answers/", views.answer_list, name="answer_list"),
    path("answers/create/", views.add_answer_view, name="answer_create"),
    path("answers/<int:pk>/edit/", views.answer_edit, name="answer_edit"),
    path("answers/<int:pk>/delete/", views.answer_delete, name="answer_delete"),
    path('answers/manage/', views.add_answer_view, name='add_answers'),

    # path('administrators_create/', views.admin_create, name='administrators_create'),
    # path('administrators/<int:pk>', views.admin_detail, name='admin_update'),
    # path('admin_delete/<int:pk>', views.AdminDelete.as_view(), name='admin_delete'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('ajax/load-months/', views.ajax_load_months, name='ajax_load_months'),   
]
