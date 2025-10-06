from django import forms
from .models import *

class FormCategoryForm(forms.ModelForm):
    class Meta:
        model = FormCategory
        fields = ['name_uz', 'name_ru', 'active', 'filial', 'for_rating']
        widgets = {
            'name_uz': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomi (UZ)'}),
            'name_ru': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomi (RU)'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'filial': forms.Select(attrs={'class': 'form-control'}),
            'for_rating': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    question_uz = forms.CharField(
        label="Savol (UZ)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Savolni kiriting"})
    )
    question_ru = forms.CharField(
        label="Savol (RU)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Вопрос на русском"})
    )
    multi_answer = forms.BooleanField(
        required=False,
        label="Ko‘p javobli savolmi?",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    text_answer = forms.BooleanField(
        required=False,
        label="Matnli javob kiritiladimi?",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    active = forms.BooleanField(
        required=False,
        label="Faol holatda",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Question
        fields = "__all__"


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['question', 'answer_uz', 'answer_ru', 'score']
        widgets = {
            'question': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Savolni tanlang'
            }),
            'answer_uz': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Javob (O'zbek tilida)"
            }),
            'answer_ru': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Javob (Rus tilida)'
            }),
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Javoblar soni'
            }),
        }