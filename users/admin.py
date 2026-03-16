from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import PhoneLoginCode, TelegramLinkToken, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ("id", "phone", "email", "is_staff", "is_active", "telegram_chat_id")
    ordering = ("phone",)
    search_fields = ("phone", "email", "telegram_chat_id")

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (
            "Contacts",
            {
                "fields": (
                    "email",
                    "telegram_chat_id",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(PhoneLoginCode)
class PhoneLoginCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "code", "is_used", "created_at")
    search_fields = ("phone", "code")


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "is_used", "created_at")
    search_fields = ("token", "user__phone")
