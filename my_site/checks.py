from .constants import *
from django.utils import timezone


def category_update_check(user, category):

    if not user or not category:
        return False

    # Add questions to the category

    accepted = False

    # Super Administrators could access to the category
    if user.profile.authority > Authority.ADMINISTRATOR:
        accepted = True

    # Only administrators who are in category.admins are allowed to update the category
    elif user in category.admins.all():
        accepted = True

    return accepted


def category_add_check(user):

    if not user:
        return False

    accepted = False

    # Users are not allowed to add any category
    if user.profile.authority > Authority.USER:
        accepted = True

    return accepted


def category_show_check(user, category):

    if not user or not category:
        return False

    accepted = False

    # Super Administrators could access to the category
    if user.profile.authority > Authority.ADMINISTRATOR:
        accepted = True

    # If the category is open, everyone is able to access to the category
    if category.is_public:
        accepted = True

    # Administrators in category admins is able to access to the category
    else:
        # If category was started, set is_public to true and set all questions authority to all
        if category.was_started():
            category.is_public = True
            for question in category.questions.all():
                question.authority = QuestionAuthority.All
                question.save()
            category.save()
            accepted = True
        else:
            if category.admins.filter(pk=user.id):
                accepted = True

    return accepted


def question_show_check(user, question):

    # Check a user authority to one question
    if not user or not question:
        return False

    accepted = False

    # Super Administrator could access to the question
    if user.profile.authority > Authority.ADMINISTRATOR:
        accepted = True

    # If user owns the question
    elif question.authority == QuestionAuthority.OWNER:
        if user == question.author:
            accepted = True

    elif question.authority == QuestionAuthority.CATEGORY:
        for category in question.category_set.all():
            if category.admins.filter(pk=user.id):
                accepted = True
                break

    elif question.authority == QuestionAuthority.All:
        accepted = True

    return accepted


def question_add_check(user):

    if not user:
        return False

    accepted = False

    # Users are not allowed to add any question
    if user.profile.authority > Authority.USER:
        accepted = True

    return accepted


def question_update_check(user, question):

    if not user:
        return False

    accepted = False

    # Super Administrators are allowed to update questions
    if user.profile.authority > Authority.ADMINISTRATOR:
        accepted = True

    # Administrators who administrate categories which contains the question are allowed to update questions
    elif question.authority == QuestionAuthority.OWNER:
        if question.author == user:
            accepted = True
    else:
        for category in user.category_set.all():
            if category.questions.filter(pk=question.id):
                accepted = True
                break

    return accepted


def exam_show_check(user, exam):
    if not user or not exam:
        return False

    accepted = False
    # Super Administrators could access to the category
    if user.profile.authority > Authority.ADMINISTRATOR:
        accepted = True

    # If the exam is open, everyone is able to access to the exam
    if exam.is_public:
        accepted = True

    elif exam.was_started():
        exam.is_public = True
        exam.save()
        accepted = True

    if exam.admins.filter(pk=user.id):
        accepted = True
    return accepted


def exam_question_show_check(user, exam, question):
    return exam_show_check(user, exam)


def exam_update_check(user, exam):
    if not user or not exam:
        return False
    accepted = False
    if user.profile.authority > Authority.ADMINISTRATOR:
        accepted = True
    if exam.admins.filter(pk=user.id):
        accepted = True
    return accepted


def exam_add_check(user):
    return category_add_check(user)