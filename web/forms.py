from django import forms
from django.contrib.auth import get_user_model

from creators.models import Creator
from posts.models import Post

User = get_user_model()


class RequestCodeForm(forms.Form):
    """Форма запроса кода по номеру телефона"""

    phone = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )


class VerifyCodeForm(forms.Form):
    """Форма подтверждения кода"""

    phone = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    code = forms.CharField(
        label="Код",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )


class CreateForm(forms.ModelForm):
    """Форма создания/редактирования профиля автора"""

    class Meta:
        model = Creator
        fields = ("display_name", "subscription_price_rub")
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя автора"}),
            "subscription_price_rub": forms.NumberInput(attrs={"class": "form-control", "min": 50}),
        }


class PostForm(forms.ModelForm):
    """Форма создания/редактирования поста"""

    class Meta:
        model = Post
        fields = ("title", "body", "is_paid")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Заголовок поста"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 8, "placeholder": "Текст поста"}),
            "is_paid": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
