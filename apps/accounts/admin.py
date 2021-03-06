from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import Account


class CustomUserAdmin(UserAdmin):
    model = Account

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (('Financeiro'), {'fields': ('can_request', 'can_aprove', 'can_pay', 'tp_user_financeiro',)}),
        (('Contato'), {'fields': ('name', 'telefone',)}),
        (('OneSignal'), {'fields': ('onesignal_id',)}),
    )


# admin.site.unregister(Account)

admin.site.register(Account, CustomUserAdmin)
