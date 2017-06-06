from django.contrib import admin
from .models import *

# Register your models here.


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


class MultipleChoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'question_text', 'published_date']
    fieldsets = [
        ('Question Information', {'fields': ['question_text']}),
        ('Explanation', {'fields': ['explanation']})
    ]
    inlines = [ChoiceInline]


admin.site.register(MultipleChoice, MultipleChoiceAdmin)
admin.site.register(Category)
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Profile)
admin.site.register(Exam)
