from django import forms
from django.contrib.auth import get_user_model

from creators.models import Creator
from posts.models import Post

User = get_user_model()


class RegisterForm(forms.ModelForm):
    """Форма регистрации пользователя"""

    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}), min_length=8
    )
    password2 = forms.CharField(
        label="Повторите пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}), min_length=8
    )

    class Meta:
        model = User
        fields = ("phone", "email")
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+79876543210"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
        }

    def clean(self):
        """Проверяем, что пароли совпадают"""

        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data

    def save(self, commit=True):
        """Создаем пользователя через кастомный менеджер"""

        user = User.objects.create_user(
            phone=self.cleaned_data["phone"], email=self.cleaned_data("email"), password=self.cleaned_data["password1"]
        )

        return user


class LoginForm(forms.Form):
    """Форма входа"""

    phone = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+79876543210"}),
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
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
