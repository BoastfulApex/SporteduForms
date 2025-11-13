from django import forms
from .models import *


from django import forms
from .models import Group, Year, Month, Filial

class GroupForm(forms.ModelForm):
    name_uz = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Guruh nomi (uz)", "class": "form-control"}
        )
    )
    name_ru = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Guruh nomi (ru)", "class": "form-control"}
        )
    )
    year = forms.ModelChoiceField(
        queryset=Year.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    month = forms.ModelChoiceField(
        queryset=Month.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    study_field = forms.ModelChoiceField(
        queryset=StudyField.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    filial = forms.ModelChoiceField(
        queryset=Filial.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Group
        fields = ["name_uz", "name_ru", "study_field", "filial", "year", "month"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Avval barcha yearlarni chiqaramiz
        self.fields["year"].queryset = Year.objects.all()

        # Agar POST orqali year kelsa -> shu yearga tegishli monthlarni filterlaymiz
        if "year" in self.data:
            try:
                year_id = int(self.data.get("year"))
                self.fields["month"].queryset = Month.objects.filter(year_id=year_id)
            except (ValueError, TypeError):
                self.fields["month"].queryset = Month.objects.none()
        elif self.instance.pk:
            # Update rejimi
            self.fields["month"].queryset = self.instance.year.months.all()
        else:
            # Default holatda bo‘sh
            self.fields["month"].queryset = Month.objects.none()


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["name", "filial"]   # cafedra yo‘q
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "O‘qituvchi ismi"}
            ),
            "filial": forms.Select(attrs={"class": "form-control"}),
        }


class StudyModuleForm(forms.ModelForm):
    class Meta:
        model = StudyModule
        fields = ["name", "study_field", "filial"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Modul nomi"}),
            "study_field": forms.Select(attrs={"class": "form-control"}),
            "filial": forms.Select(attrs={"class": "form-control"}),
        }
        
        
class StudyModuleUploadForm(forms.Form):
    filial = forms.ModelChoiceField(
        queryset=Filial.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    study_field = forms.ModelChoiceField(
        queryset=StudyField.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"})
    )
    file = forms.FileField(
        widget=forms.FileInput(attrs={"class": "form-control"})
    )


class AssignTeacherForm(forms.ModelForm):
    class Meta:
        model = GroupModuleTeacher
        fields = ["teacher"]
        widgets = {
            "teacher": forms.Select(attrs={"class": "form-control"}),
        }
        
class GroupModuleTeacherActiveForm(forms.ModelForm):
    class Meta:
        model = GroupModuleTeacher
        fields = ["active"]
        widgets = {
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        

class MonthSelectForm(forms.Form):
    year = forms.ModelChoiceField(
        queryset=Year.objects.all().order_by('-year'),
        label="Yilni tanlang",
        required=True
    )
    month = forms.ModelChoiceField(
        queryset=Month.objects.none(),
        label="Oyni tanlang",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Yil tanlangan bo‘lsa, shu yilga tegishli oylar chiqsin
        if 'year' in self.data:
            try:
                year_id = int(self.data.get('year'))
                self.fields['month'].queryset = Month.objects.filter(year_id=year_id).order_by('month')
            except (ValueError, TypeError):
                pass
        elif self.initial.get('year'):
            year = self.initial.get('year')
            self.fields['month'].queryset = Month.objects.filter(year=year).order_by('month')
            


class ScheduleForm(forms.Form):
    year = forms.ModelChoiceField(
        queryset=Year.objects.all(),
        label="Yil",
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "id": "id_year",
        })
    )

    month = forms.ModelChoiceField(
        queryset=Month.objects.none(),
        label="Oy",
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "id": "id_month",
        })
    )

    filial = forms.ModelChoiceField(
        queryset=Filial.objects.all(),
        label="Filial",
        widget=forms.Select(attrs={
            "class": "form-control select2",
            "id": "id_filial",
        })
    )

    # Agar keyinchalik buttonni ham form ichida style qilish kerak bo‘lsa:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agar form POST orqali qayta ochilsa, yil tanlanganda oylar chiqsin
        if 'year' in self.data:
            try:
                year_id = int(self.data.get('year'))
                self.fields['month'].queryset = Month.objects.filter(year_id=year_id)
            except (ValueError, TypeError):
                pass# class FilialForm(forms.ModelForm):
#     filial = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Slider nomi uz",
#                 "class": "form-control",
#                 'readonly': 'readonly'
#             }
#         ))

#     number = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Slider nomi ru",
#                 "class": "form-control",
#                 'readonly': 'readonly',
#     }
#         ))
#     image = forms.ImageField(
#       widget=forms.FileInput()
#     )

#     class Meta:
#         model = Filial
#         fields = "__all__"


# class SubCategoryForm(forms.ModelForm):
#     name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Slider nomi uz",
#                 "class": "form-control",
#                 'readonly': 'readonly'
#             }
#         ))

#     code = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#                 'readonly': 'readonly',
#             }
#         ))

#     category = forms.ModelChoiceField(
#         widget=forms.Select(
#             attrs={
#                 "class": "form-control",
#                 'readonly': 'readonly'
#             }
#         ),
#         queryset=Category.objects.all())

#     image = forms.ImageField(
#       widget=forms.FileInput()
#     )

#     class Meta:
#         model = SubCategory
#         fields = "__all__"


# class ManufacturerForm(forms.ModelForm):
#     manufacturer_name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#                 'readonly': 'readonly'
#             }
#         ))

#     code = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#                 'readonly': 'readonly',
#             }
#         ))
#     image = forms.ImageField(
#       widget=forms.FileInput()
#     )

#     class Meta:
#         model = Category
#         fields = "__all__"


# class ProductForm(forms.ModelForm):
#     itemname = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     itemcode = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     description = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Maxsulot izohi",
#                 "class": "form-control",
#             }
#         ))
#     price = forms.FloatField(
#         widget=forms.NumberInput(
#             attrs={
#                 "placeholder": "Maxsulot narxi",
#                 "class": "form-control",
#             }
#         ))
#     image = forms.ImageField(
#       widget=forms.FileInput()
#     )
#     top = forms.BooleanField(
#         label="Top 100",
#         required=False,
#         initial=False,
#         widget=forms.CheckboxInput(attrs={'class': 'custom-class'}),
#     )

#     class Meta:
#         model = Product
#         fields = ["itemname", "itemcode", "description", "price", "image", "top"]


# class CashbackForm(forms.ModelForm):
#     PERIOD_TYPES = (
#         (MONTH, MONTH),
#         (SEASON, SEASON),
#         (YEAR, YEAR)
#     )

#     name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     period = forms.ChoiceField(
#         choices=PERIOD_TYPES,
#         widget=forms.Select(
#             attrs={
#                 "class": "form-control",
#                 'readonly': 'readonly'
#             }
#         ))
#     summa = forms.FloatField(
#         widget=forms.NumberInput(
#             attrs={
#                 "placeholder": "Summa",
#                 "class": "form-control",
#             }
#         ))
#     persent = forms.FloatField(
#         widget=forms.NumberInput(
#             attrs={
#                 "placeholder": "Summa",
#                 "class": "form-control",
#             }
#         ))

#     class Meta:
#         model = Product
#         fields = ["name", "summa", "period", "persent"]


# class NotificationForm(forms.ModelForm):
#     name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Bildirishnoma Sarlavhasi",
#                 "class": "form-control",
#             }
#         ))

#     message = forms.CharField(
#         widget=forms.Textarea(
#             attrs=
#             {
#                 "placeholder": "Xabar matni",
#                 "class": "form-control",
#             }
#         ))

#     class Meta:
#         model = Notification
#         fields = '__all__'


# class SaleForm(forms.ModelForm):
#     name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     expiration_date = forms.DateField(
#         widget=forms.DateInput(
#             attrs={
#                 "class": "form-control",
#                 "type": "date",
#                 "style": "width: 200px;"
#             }
#         )
#     )
#     required_product = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     required_quantity = forms.FloatField(
#         widget=forms.NumberInput(
#             attrs={
#                 "placeholder": "Kerakli miqdor",
#                 "class": "form-control",
#             }
#         ))
#     gift_quantity = forms.FloatField(
#         widget=forms.NumberInput(
#             attrs={
#                 "placeholder": "Sovg'a miqdori",
#                 "class": "form-control",
#             }
#         ))
#     gift_product = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))

#     image = forms.ImageField(
#       widget=forms.FileInput()
#     )

#     description = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#     ))

#     class Meta:
#         model = Sale
#         fields = ["name", "expiration_date", "required_quantity", "gift_quantity", 'image', 'description']


# class StoryCategoryForm(forms.ModelForm):
#     name = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     image = forms.ImageField(
#       widget=forms.FileInput()
#     )
#     index = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))

#     class Meta:
#         model = StoryCategory
#         fields = '__all__'


# class StoryForm(forms.ModelForm):
#     title = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "class": "form-control",
#             }
#         ))
#     file = forms.FileField(
#       widget=forms.FileInput(
#           attrs={
#               "class": "form-control-file",
#           }
#       )
#     )
#     story_category = forms.ModelChoiceField(
#         widget=forms.Select(
#             attrs={
#                 "class": "form-control",
#             }
#         ),
#         queryset=StoryCategory.objects.all(),
#         empty_label=None
#     )

#     class Meta:
#         model = Story
#         fields = '__all__'

#     # def __init__(self, *args, **kwargs):
#     #     super(StoryForm, self).__init__(*args, **kwargs)
#     #     self.fields['story_category'].choices = [(category.id, category.name) for category in StoryCategory.objects.all()]
