from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Book, Member, Loan, Fine
from django import forms
from django.contrib.auth.hashers import make_password

# Custom form for Member creation with User fields
class MemberCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    name = forms.CharField(max_length=180, required=True, label='Name')
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Member
        fields = ['member_type']

    def save(self, commit=True):
        # Split the name into first and last name
        full_name = self.cleaned_data['name'].strip()
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        user = User(
            username=self.cleaned_data['username'],
            first_name=first_name,
            last_name=last_name,
            email=self.cleaned_data.get('email', ''),
            password=make_password(self.cleaned_data['password'])
        )
        user.save()
        member = super().save(commit=False)
        member.user = user
        if commit:
            member.save()
        return member

class MemberAdmin(admin.ModelAdmin):
    form = MemberCreationForm
    list_display = ('id', 'user', 'member_type')
    # Hide the 'user' field from the form since we are creating it inline
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'user' in form.base_fields:
            form.base_fields['user'].widget = forms.HiddenInput()
        return form

admin.site.register(Book)
admin.site.register(Member, MemberAdmin)
admin.site.register(Loan)
admin.site.register(Fine)
