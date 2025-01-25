from django.contrib import admin

# Register your models here.
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from discordlogin.models import DiscordUser, Item


from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from wagtail.images.models import Image
from wagtail.models import Page
from wagtail.documents.models import Document
from taggit.models import Tag

from discordlogin.accounts.forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = DiscordUser
    list_display = ['token']

    class Meta:
        model = DiscordUser
        fields = ('id', 'token', 'is_superuser','is_staff')


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = DiscordUser
        fields = ('id', 'discord_tag', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["token"]


class UserAdmin(BaseUserAdmin):
    readonly_fields = ('id', 'discord_tag', 'token')

    # The forms to add and change user instances
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    #add_form = UserCreationForm

    

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'discord_tag', 'is_staff', 'is_superuser')
    list_filter = ('is_superuser','is_staff',)
    fieldsets = (
        (None, {'fields': ('id', 'discord_tag')}),
        ('Permissions', {'fields': ('is_staff','is_superuser',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'date_of_birth', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('id',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(DiscordUser, UserAdmin)
admin.site.register(Item)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
admin.site.unregister(Document)
admin.site.unregister(Image)
admin.site.unregister(Tag)

#admin.site.unregister(User)######