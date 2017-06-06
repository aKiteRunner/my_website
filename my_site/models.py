from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import timedelta
from .constants import Authority, QuestionAuthority

# Create your models here.


class MultipleChoice(models.Model):
    question_text = models.CharField(max_length=384)
    published_date = models.DateTimeField('published date', auto_now_add=True)
    explanation = models.CharField(max_length=384, null=True, blank=True)
    authority = models.SmallIntegerField('authority', default=QuestionAuthority.OWNER)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self, days):
        return self.published_date >= timezone.now() - timedelta(days)

    def abbreviated_text(self):
        if len(self.question_text) < 30:
            return self.question_text
        else:
            return self.question_text[:30] + '...'


class Choice(models.Model):
    question = models.ForeignKey(MultipleChoice, on_delete=models.CASCADE, null=True, blank=True)
    choice_text = models.CharField(max_length=256)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.choice_text


class Category(models.Model):
    category_text = models.CharField(max_length=64, unique=True)
    questions = models.ManyToManyField(MultipleChoice, blank=True)
    admins = models.ManyToManyField(User, blank=True)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.category_text

    def was_started(self):
        return self.start_time <= timezone.now()

    def was_ended(self):
        return self.end_time <= timezone.now()

    def category_state(self):
        if not self.was_started():
            return '即将开放'
        elif self.was_started() and not self.was_ended():
            return '已开放'
        else:
            return '已关闭'

    class Meta:
        verbose_name_plural = 'Categories'


class Profile(models.Model):
    user = models.OneToOneField(User)
    authority = models.SmallIntegerField('Authority', default=Authority.USER)
    student_id = models.CharField(max_length=24, null=True, blank=True)
    school = models.CharField(max_length=24, null=True, blank=True)
    introduction = models.CharField(max_length=140, null=True, blank=True)

    def is_user(self):
        return self.authority == Authority.USER

    def is_administrator(self):
        return self.authority >= Authority.ADMINISTRATOR


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    question = models.ForeignKey(MultipleChoice, on_delete=models.CASCADE, blank=True)
    answer_text = models.CharField(max_length=640, null=True, blank=True)
    submitted_date = models.DateTimeField('Submitted time', auto_now_add=True)
    grade = models.SmallIntegerField('Grade', null=True, blank=True)

    def __str__(self):
        if self.answer_text:
            return self.answer_text
        else:
            return 'None'

    def get_grade(self):
        if self.grade is None:
            return '无'
        else:
            return str(self.grade)


class Exam(models.Model):
    category_text = models.CharField(max_length=64, unique=True)
    questions = models.ManyToManyField(MultipleChoice, blank=True)
    admins = models.ManyToManyField(User, blank=True)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.category_text

    def was_started(self):
        return self.start_time <= timezone.now()

    def was_ended(self):
        return self.end_time <= timezone.now()

    def category_state(self):
        if not self.was_started():
            return '即将开放'
        elif self.was_started() and not self.was_ended():
            return '已开放'
        else:
            return '已关闭'


class ExamSubmission(Submission):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, blank=True)

    def get_grade(self):
        if self.grade is None or not self.exam.was_ended():
            return '无'
        else:
            return self.grade


class Grade(models.Model):
    question = models.ForeignKey(MultipleChoice, on_delete=models.CASCADE, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, blank=True)
    grade = models.SmallIntegerField('Grade')
