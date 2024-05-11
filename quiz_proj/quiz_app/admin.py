from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import *


# over riding the default behaviour of Custom user model to looks cleaner interface
# in the admin panel


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model with no username field."""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'full_name', 'is_staff')
    search_fields = ('email', 'full_name')
    ordering = ('email',)


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(QuizForm)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(UserAnswer)
admin.site.register(UserResult)
admin.site.register(UserGivenQuizes)

# and also we can write like this
# admin.site.register(settings.AUTH_USER_MODEL)
