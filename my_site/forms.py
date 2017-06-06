from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError
from .models import *
from datetime import datetime


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_text', 'start_time', 'end_time']

    def clean_start_time(self):
        try:
            start_time = self.cleaned_data['start_time']
        except KeyError:
            raise ValidationError('开始时间不能为空')
        return start_time

    def clean_end_time(self):
        try:
            start_time = self.cleaned_data['start_time']
            end_time = self.cleaned_data['end_time']
        except KeyError:
            raise ValidationError('结束时间不能为空')

        # Ensure end time > start time
        if end_time <= start_time:
            raise ValidationError('时间不合法')
        return end_time


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['category_text', 'start_time', 'end_time']

    def clean_start_time(self):
        try:
            start_time = self.cleaned_data['start_time']
        except KeyError:
            raise ValidationError('开始时间不能为空')
        return start_time

    def clean_end_time(self):
        try:
            start_time = self.cleaned_data['start_time']
            end_time = self.cleaned_data['end_time']
        except KeyError:
            raise ValidationError('结束时间不能为空')

        # Ensure end time > start time
        if end_time < start_time:
            raise ValidationError('时间不合法')
        return end_time


class MultipleChoiceForm(forms.ModelForm):
    class Meta:
        model = MultipleChoice
        fields = ['question_text', 'explanation', 'author']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct', 'question']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput(), min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        # Ensure password length is not less than eight characters
        if not (8 <= len(password) <= 16):
            raise ValidationError('密码格式错误')
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password', '')
        password2 = self.cleaned_data.get('password2', '')

        # Ensure the two password is the same
        if password != password2:
            raise ValidationError('密码不匹配')
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError('请正确填写邮箱地址')
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['school', 'student_id', 'introduction']
