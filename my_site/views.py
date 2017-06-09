from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from .forms import *
from .checks import *
from collections import defaultdict
import random

# Create your views here.


def index(request):
    return render(request, 'my_site/index.html')


def register(request):
    context = dict()

    if request.method == 'POST':

        # Validate the form
        user_form = UserForm(request.POST)

        if user_form.is_valid():

            user = user_form.save()

            # password need to be hashed
            user.set_password(user.password)
            user.save()

            # When someone registered successfully, redirect them to index page
            login(request, user)
            return HttpResponseRedirect(reverse('index'))

        else:

            # The form is not valid, show the errors
            error = user_form.errors
            messages.error(request, error)

    # If the method is not post, show the register form
    # If any exception is caught, show the form and errors
    return render(request, 'my_site/register.html', context)


def user_login(request):
    context = dict()

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                # When user signed in, redirect them to index page
                return HttpResponseRedirect(reverse('index'))

            else:

                # User could be not active
                errors = '用户未激活'
                messages.error(request, errors)

        else:

            # if username and password not match, user is None
            errors = '密码错误'
            messages.error(request, errors)

    # if the method is not post show the form.
    # if any exception is caught, show the form and errors
    return render(request, 'my_site/login.html', context)


@login_required
def user_logout(request):
    logout(request)

    # When users signed out, redirect them to index page
    return HttpResponseRedirect(reverse('index'))


@login_required
def edit_user_profile(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=profile)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, '表单不合法')
    context = dict()
    context['user'] = user
    return render(request, 'my_site/edit_user_profile.html', context)


@login_required
def edit_user_authority(request):
    context = dict()
    user = request.user
    if request.method == 'POST':
        # Parse form
        try:
            normal_user_name = request.POST['normal_user'].strip()
            category_id = request.POST['category']
            exam_id = request.POST['exam']
            if category_id:
                category_id = int(category_id)
            if exam_id:
                exam_id = int(exam_id)
            normal_user = User.objects.get(username=normal_user_name)
            if category_id:
                category = Category.objects.get(pk=category_id)
                if category_update_check(user, category):
                    # Edit user authority
                    if normal_user.profile.authority == Authority.USER:
                        normal_user.profile.authority = Authority.ADMINISTRATOR
                        normal_user.save()
                    category.admins.add(normal_user)
                    category.save()
                else:
                    messages.error(request, '没有权限')
            if exam_id:
                exam = Exam.objects.get(pk=exam_id)
                if exam_update_check(user, exam):
                    # Edit user authority
                    if normal_user.profile.authority == Authority.USER:
                        normal_user.profile.authority = Authority.ADMINISTRATOR
                        normal_user.save()
                    exam.admins.add(normal_user)
                    exam.save()
        except (KeyError, ObjectDoesNotExist, ValueError):
            messages.error(request, '输入不合法')
        messages.info(request, '操作成功')
    return render(request, 'my_site/index.html', context)


@login_required
def edit_user_password(request):
    user = request.user
    if request.method == 'POST':
        try:
            old_password = request.POST.get('old_password')
            password1 = request.POST.get('password')
            password2 = request.POST.get('password2')
            if not user.check_password(old_password):
                raise ValidationError('密码错误')
            if not (8 <= len(password1) <= 16):
                raise ValidationError('密码格式错误')
            if password1 != password2:
                raise ValidationError('密码不匹配')
            user.set_password(password1)
            user.save()
            messages.info(request, '保存成功')
        except KeyError:
            messages.error(request, '请正确填写密码')
        except ValidationError as e:
            messages.error(request, e.message)
    return render(request, 'my_site/edit_password.html', context={})


@login_required
def show_user_profile(request, user_id):
    context = dict()
    user = get_object_or_404(User, pk=user_id)
    context['show_user'] = user
    return render(request, 'my_site/user_profile.html', context)


@login_required
def show_category(request, category_id):

    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (KeyError, ValueError):
        page = 1

    context = dict()
    user = request.user

    # If category is not exist, or user is not able to access to the category, return 404 not found
    category = get_object_or_404(Category, pk=category_id)
    if not category_show_check(user, category):
        return Http404()

    questions = category.questions.all()
    if not len(questions):
        total_page = 1
    else:
        total_page = (len(questions) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    questions = questions[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['questions'] = questions
    context['page'] = page
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page

    return render(request, 'my_site/category_detail.html', context)


@login_required
def show_exam(request, exam_id):

    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (KeyError, ValueError):
        page = 1

    context = dict()
    user = request.user

    # If exam is not exist, or user is not able to access to the category, return 404 not found
    exam = get_object_or_404(Exam, pk=exam_id)
    if not exam_show_check(user, exam):
        return Http404()

    questions = exam.questions.all()
    if not len(questions):
        total_page = 1
    else:
        total_page = (len(questions) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    questions = questions[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['questions'] = questions
    context['exam'] = exam
    context['page'] = page
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page

    return render(request, 'my_site/exam_detail.html', context)


@login_required
def show_exam_question(request, exam_id, question_id):
    context = dict()
    # Check authority
    user = request.user

    # If the question or exam is not exist, or user is not able to access to question, return 404 not found
    question = get_object_or_404(MultipleChoice, pk=question_id)
    exam = get_object_or_404(Exam, pk=exam_id)
    grade = Grade.objects.filter(exam=exam_id, question=question_id)
    if not exam_show_check(user, exam) or not exam_question_show_check(user, exam, question):
        return Http404()

    context['question'] = question
    context['exam'] = exam
    return render(request, 'my_site/exam_question_detail.html', context)


@login_required
def show_question(request, question_id):

    context = dict()
    # Check authority
    user = request.user

    # If the question is not exist, or user is not able to access to question, return 404 not found
    question = get_object_or_404(MultipleChoice, pk=question_id)
    if not question_show_check(user, question):
        return Http404()

    context['question'] = question
    return render(request, 'my_site/question_detail.html', context)


@login_required
def show_categories(request):

    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1

    context = dict()
    user = request.user
    categories = Category.objects.all()
    filtered_category = list()

    # Filter the categories
    for category in categories:
        if category_show_check(user, category):
            filtered_category.append(category)

    # Show some categories
    if not len(filtered_category):
        total_page = 1
    else:
        total_page = (len(filtered_category) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    filtered_category = filtered_category[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['errors'] = None
    context['categories'] = filtered_category
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page

    return render(request, 'my_site/categories.html', context)


@login_required
def show_exams(request):
    # Check the parameter, if page is invalid page = 1
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1

    context = dict()
    user = request.user
    exams = Exam.objects.all()
    # Filter the exams
    filtered_exam = list(filter(lambda exam: exam_show_check(user, exam), exams))
    if not len(filtered_exam):
        total_page = 1
    else:
        total_page = (len(filtered_exam) - 1) // PAGE_MAX + 1
    pages, prepage, next_page = get_pages(total_page, page)
    filtered_exam = filtered_exam[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['exams'] = filtered_exam
    context['pages'] = pages
    context['pre_page'] = prepage
    context['next_page'] = next_page
    return render(request, 'my_site/exams.html', context)


@login_required
def show_questions(request):

    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1

    context = dict()
    user = request.user
    questions = MultipleChoice.objects.all()
    filter_questions = list()

    # Filter the questions
    for question in questions:
        if question_show_check(user, question):
            filter_questions.append(question)

    # Show some questions
    if not len(filter_questions):
        total_page = 1
    else:
        total_page = (len(filter_questions) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    filter_questions = filter_questions[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['questions'] = filter_questions
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page

    return render(request, 'my_site/questions.html', context)


@login_required
def add_category(request):
    context = dict()
    user = request.user

    if category_add_check(user):

        # Check authority

        if request.method == 'POST':

            # Validate the form
            category_form = CategoryForm(request.POST)

            if category_form.is_valid():

                # If the form is valid, save the form and
                # add the user to category admins
                # Check the questions, if question is exist, add to category
                question_ids = request.POST.getlist('question_id', list())
                for question_id in question_ids:
                    if not MultipleChoice.objects.filter(pk=question_id):
                        messages.error(request, '问题不存在')
                        return render(request, 'my_site/add_category.html', context)
                else:
                    category = category_form.save()
                    category.admins.add(user)
                    for question_id in question_ids:
                        question = MultipleChoice.objects.get(pk=question_id)
                        category.questions.add(question)

                        # Set question authority to CATEGORY
                        if question.authority == QuestionAuthority.OWNER:
                            question.authority = QuestionAuthority.CATEGORY
                            question.save()
                    category.save()

                    # When a category is created successfully,
                    # redirect user to category index page
                    messages.info(request, '创建成功')
                    return HttpResponseRedirect(reverse('categories'))

            else:

                # If the form is invalid, show user the errors
                messages.error(request, '表单信息不合法')

        # If the method is not post, show the form
        # If any exception is caught, show the form and errors
        return render(request, 'my_site/add_category.html', context)

    else:

        # If users do not have permission to add category,
        # redirect them to category index page
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('categories'))


@login_required
def add_exam(request):
    context = dict()
    user = request.user

    if exam_add_check(user):

        # Check authority
        if request.method == 'POST':

            # Validate the form
            exam_form = ExamForm(request.POST)
            if exam_form.is_valid():
                # If the form is valid, save the form and add the user to exam admins
                # Check the questions, add question to exam, and set grade
                question_ids = request.POST.getlist('question_id', list())
                grades = request.POST.getlist('grade', list())
                # Ensure every question has a grade
                if len(question_ids) != len(grades):
                    messages.error(request, '请为每个问题都填入分数')
                    return render(request, 'my_site/add_exam.html', context)

                for question_id in question_ids:
                    if not MultipleChoice.objects.filter(pk=question_id):
                        messages.error(request, '问题不存在', context)
                        return render(request, 'my_site/add_exam.html', context)

                for question_grade in grades:
                    try:
                        question_grade = int(question_grade)
                        if not 0 <= question_grade <= 100:
                            raise ValueError
                    except ValueError:
                        messages.error(request, '请输入合法分数0~100')
                        return render(request, 'my_site/add_exam.html', context)

                exam = exam_form.save()
                exam.admins.add(user)
                for question_id, question_grade in zip(question_ids, grades):
                    question = MultipleChoice.objects.get(pk=question_id)
                    exam.questions.add(question)
                    grade = Grade.objects.create(exam=exam, question=question, grade=int(question_grade))
                    grade.save()
                exam.save()
                messages.info(request, '创建成功')
                return HttpResponseRedirect(reverse('exams'))
            else:
                # If the form is invalid, show user the errors
                messages.error(request, '表单信息不合法')
        return render(request, 'my_site/add_exam.html', context)
    else:
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('exams'))


@login_required
def add_question(request):
    context = dict()
    user = request.user
    # Check authority
    if question_add_check(user):

        if request.method == 'POST':

            # Validate the form
            data = dict()
            data['question_text'] = request.POST.get('question_text', '')
            data['explanation'] = request.POST.get('explanation', '')
            data['author'] = user.id
            question_form = MultipleChoiceForm(data)

            if question_form.is_valid():

                question = question_form.save()
                question.author = user
                question.save()

                # Extract choice form
                choice_text_list = request.POST.getlist('choice_text', list())
                is_correct_list = request.POST.getlist('is_correct', list())

                for i in range(len(choice_text_list)):
                    choice_text = choice_text_list[i]
                    if str(i) in is_correct_list:
                        is_correct = 'on'
                    else:
                        is_correct = None

                    data = dict()
                    data['choice_text'] = choice_text
                    data['is_correct'] = is_correct
                    data['question'] = question.id
                    choice_form = ChoiceForm(data)

                    # Save the choice, if the choice form is valid
                    # Ignore the invalid choice
                    if choice_form.is_valid():
                        choice_form.save()
                    else:
                        messages.error(request, '表单信息不合法')
                return HttpResponseRedirect(reverse('questions'))

            else:

                # If the form is invalid, show user the errors
                messages.error(request, '表单信息不合法')

        return render(request, 'my_site/add_question.html', context)

    else:

        # If users do not have permission to add question,
        # redirect them to question index page
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('questions'))


@login_required
def update_category(request, category_id):
    context = dict()
    category = get_object_or_404(Category, pk=category_id)
    questions = category.questions.all()
    user = request.user
    context['category'] = category
    context['questions'] = questions

    #  Check authority
    if category_update_check(user, category):

        if request.method == 'POST':

            # Validate the form
            category_form = CategoryForm(request.POST)
            category_title = category.category_text
            category.category_text = ''
            category.save()

            if category_form.is_valid():

                # If the form is valid, save the form
                # Check the questions, if question is exist, add to category
                question_ids = request.POST.getlist('question_id', list())
                for question_id in question_ids:
                    if not MultipleChoice.objects.filter(pk=question_id):
                        messages.error(request, '题目不存在')
                        category.category_text = category_title
                        category.save()
                        return render(request, 'my_site/update_category.html', context)
                else:
                    category.category_text = category_form.cleaned_data['category_text']
                    category.start_time = category_form.cleaned_data['start_time']
                    category.end_time = category_form.cleaned_data['end_time']
                    category.save()
                    category.questions.clear()
                    for question_id in question_ids:
                        question = MultipleChoice.objects.get(pk=question_id)
                        category.questions.add(question)

                        # Set question authority to CATEGORY
                        if question.authority == QuestionAuthority.OWNER:
                            question.authority = QuestionAuthority.CATEGORY
                            question.save()
                    category.save()

                # When a category is updated successfully,
                # redirect user to category index page
                messages.info(request, '修改成功')
                return HttpResponseRedirect(reverse('categories'))

            else:

                # If the form is invalid, show user the errors
                category.category_text = category_title
                category.save()
                messages.error(request, '表单信息不合法')

        # If the method is not post, show the form
        # If any exception is caught, show the form and errors
        context['category'] = category
        context['questions'] = questions
        return render(request, 'my_site/update_category.html', context)

    else:

        # If users do not have permission to add category,
        # redirect them to category index page
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('categories'))


@login_required
def update_exam(request, exam_id):
    context =dict()
    exam = get_object_or_404(Exam, pk=exam_id)
    questions = exam.questions.all().order_by('id')
    user = request.user
    grades = Grade.objects.filter(exam=exam_id).order_by('question')
    context['exam'] = exam
    context['questions'] = zip(questions, grades)
    # Check authority
    if exam_update_check(user, exam):
        if request.method == 'POST':
            # Validate the form
            exam_form = ExamForm(request.POST)
            exam_title = exam.category_text
            exam.category_text = ''
            exam.save()
            if exam_form.is_valid():
                # If the form is valid, save the form
                # Check the questions, if question is exist, add to category
                question_ids = request.POST.getlist('question_id', list())
                grades = request.POST.getlist('grade', list())
                if len(question_ids) != len(grades):
                    messages.error(request, '请为每个问题都填入分数')
                    exam.category_text = exam_title
                    exam.save()
                    return render(request, 'my_site/update_exam.html', context)
                for question_grade in grades:
                    try:
                        question_grade = int(question_grade)
                        if not 0 <= question_grade <= 100:
                            raise ValueError
                    except ValueError:
                        messages.error(request, '请输入合法分数0~100')
                        return render(request, 'my_site/update_exam.html', context)
                for question_id in question_ids:
                    if not MultipleChoice.objects.filter(pk=question_id):
                        messages.error(request, '题目不存在')
                        exam.category_text = exam_title
                        exam.save()
                        return render(request, 'my_site/update_exam.html', context)
                else:
                    exam.category_text = exam_form.cleaned_data['category_text']
                    exam.start_time = exam_form.cleaned_data['start_time']
                    exam.end_time = exam_form.cleaned_data['end_time']
                    exam.save()
                    exam.questions.clear()
                    Grade.objects.filter(exam=exam_id).delete()
                    for question_id, question_grade in zip(question_ids, grades):
                        question = MultipleChoice.objects.get(pk=question_id)
                        grade = Grade.objects.create(question=question, exam=exam, grade=int(question_grade))
                        grade.save()
                        exam.questions.add(question)
                    exam.save()
                # When a exam is updated successfully, redirect user to exam index page
                messages.info(request, '修改成功')
                return HttpResponseRedirect(reverse('exams'))
            else:
                # If the form is invalid, show user the errors
                exam.category_text = exam_title
                exam.save()
                messages.error(request, '表单信息不合法')
                return render(request, 'my_site/update_exam.html', context)
        else:
            grade = Grade.objects.filter(exam=exam_id).order_by('question')
            context['exam'] = exam
            context['questions'] = zip(questions, grade)
            return render(request, 'my_site/update_exam.html', context)
    else:
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('exams'))


@login_required
def update_question(request, question_id):

    context = dict()
    question = get_object_or_404(MultipleChoice, pk=question_id)
    choices = question.choice_set.all()
    user = request.user

    # Check authority
    if question_update_check(user, question):

        if request.method == 'POST':

            # Validate the form
            question_form = MultipleChoiceForm(request.POST)

            if question_form.is_valid():

                question.question_text = question_form.cleaned_data['question_text']
                question.explanation = question_form.cleaned_data['explanation']
                question.save()

                # Extract choice form
                choice_text_list = request.POST.getlist('choice_text', list())
                is_correct_list = request.POST.getlist('is_correct', list())

                max_length = max((len(choice_text_list)), len(choices))
                min_length = min((len(choice_text_list)), len(choices))

                for i in range(min_length):
                    choice_text = choice_text_list[i]
                    if str(i) in is_correct_list:
                        is_correct = 'on'
                    else:
                        is_correct = None

                    data = dict()
                    data['choice_text'] = choice_text
                    data['is_correct'] = is_correct
                    data['question'] = question.id
                    choice_form = ChoiceForm(data)

                    # Save the choice, if the choice form is valid
                    # Ignore the invalid choice
                    if choice_form.is_valid():
                        choices[i].choice_text = choice_form.cleaned_data['choice_text']
                        choices[i].is_correct = choice_form.cleaned_data['is_correct']
                        choices[i].save()
                    else:
                        messages.error(request, choice_form.errors)

                # If choices length is shortened, delete choices, or create choices
                if len(choices) > len(choice_text_list):
                    for i in range(min_length, max_length):
                        choices[i].delete()
                else:
                    for i in range(min_length, max_length):
                        choice_text = choice_text_list[i]
                        if str(i) in is_correct_list:
                            is_correct = 'on'
                        else:
                            is_correct = None

                        data = dict()
                        data['choice_text'] = choice_text
                        data['is_correct'] = is_correct
                        data['question'] = question.id
                        choice_form = ChoiceForm(data)

                        # Save the choice, if the choice form is valid
                        # Ignore the invalid choice
                        if choice_form.is_valid():
                            choice_form.save()
                        else:
                            messages.error(request, '表单信息不合法')

                return HttpResponseRedirect(reverse('questions'))

            else:

                # If the form is invalid, show user the errors
                messages.error(request, '表单信息不合法')

        context['question'] = question
        context['choices'] = choices
        return render(request, 'my_site/update_question.html', context)

    else:

        # If users do not have permission to add question,
        # redirect them to question index page
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('questions'))


@login_required
def answer_submit(request, question_id):
    context = dict()

    # Check user authority
    user = request.user

    # If the question is not exist, or user is not able to access to question, return 404 not found
    question = get_object_or_404(MultipleChoice, pk=question_id)
    if not question_show_check(user, question):
        return Http404()

    if request.method == 'POST':

        # If choice in POST, check the answer, or save the submission
        if 'choice' in request.POST.keys():

            choice_ids = request.POST.getlist('choice')
            correct_choices = question.choice_set.filter(is_correct=True)

            # If the answer is correct, grade set to 100
            grade = 100
            if len(choice_ids) > len(correct_choices):
                grade = 0

            else:
                for correct_choice in correct_choices:
                    for choice_id in choice_ids:
                        if choice_id == str(correct_choice.id):
                            break
                    else:
                        grade = 0
                        break
            answer_text = ''
            for choice_id in choice_ids:
                answer_text += str(Choice.objects.get(pk=choice_id)) + '\r\n'
            submission = Submission.objects.create(user=user, question=question, grade=grade, answer_text=answer_text)
            submission.save()
            return HttpResponseRedirect(reverse('submission', args=(question_id, )))

        # If there is no choice, save answer text for administrator
        else:
            try:
                answer_text = request.POST['answer_text']
                submission = Submission.objects.create(user=user, question=question, answer_text=answer_text)
                answer = zip(answer_text.split('\r\n'), question.explanation.split('\r\n'))
                grade = 100 * sum(1 if x1 == x2 else 0 for x1, x2 in answer) / len(question.explanation.split('\r\n'))
                submission.grade = grade
                submission.save()
                return HttpResponseRedirect(reverse('submission', args=(question_id, )))
            except KeyError:
                messages.error(request, '答案不能为空')

    context['question'] = question
    return render(request, 'my_site/question_detail.html', context)


@login_required
def exam_answer_submit(request, exam_id, question_id):
    context = dict()

    # Check user authority
    user = request.user

    # If the question or exam is not exist, or user is not able to access to question or exam, return 404 not found
    question = get_object_or_404(MultipleChoice, pk=question_id)
    exam = get_object_or_404(Exam, pk=exam_id)
    if not exam_show_check(user, exam) or not exam_question_show_check(user, exam, question):
        return Http404()

    if request.method == 'POST':

        # If choice in POST, check the answer
        if 'choice' in request.POST.keys():
            choice_ids = request.POST.getlist('choice')
            correct_choices = question.choice_set.filter(is_correct=True)

            # If the answer is correct, grade set to Grade
            grade = Grade.objects.get(question=question_id, exam=exam_id).grade
            if len(choice_ids) > len(correct_choices):
                grade = 0
            else:
                for correct_choice, choice_id in zip(correct_choices, choice_ids):
                    if choice_id != str(correct_choice.id):
                        grade = 0
                        break

            answer_text = ''
            for choice_id in choice_ids:
                answer_text += str(Choice.objects.get(pk=choice_id)) + '\r\n'
            submission = ExamSubmission.objects.create(
                user=user, question=question, exam=exam, grade=grade, answer_text=answer_text)
            submission.save()
            return HttpResponseRedirect(reverse('exam_submission', args=(exam_id, question_id)))

    # If there is no choice, save answer text
        else:
            try:
                answer_text = request.POST['answer_text']
                answer = zip(answer_text.split('\r\n'), question.explanation.split('\r\n'))
                grade = Grade.objects.get(question=question_id, exam=exam_id).grade
                grade *= sum(1 if x1 == x2 else 0 for x1, x2 in answer) / len(question.explanation.split('\r\n'))
                submission = ExamSubmission.objects.create(
                    user=user, question=question, exam=exam, grade=grade, answer_text=answer_text
                )
                submission.save()
                return HttpResponseRedirect(reverse('exam_submission', args=(exam_id, question_id)))
            except KeyError:
                messages.error(request, '答案不能为空')

    context['exam'] = exam
    context['question'] = question
    return render(request, 'my_site/exam_question_detail.html', context)


@login_required
def show_exam_question_submissions(request, exam_id, question_id):

    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1

    context = dict()
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    question = get_object_or_404(MultipleChoice, pk=question_id)

    # Check authority
    # If user is administrator, show all submissions, or show submissions of the user
    if exam_update_check(user, exam):
        submissions = ExamSubmission.objects.filter(exam=exam_id, question=question_id).order_by('-id')
    else:
        submissions = ExamSubmission.objects.filter(exam=exam_id, question=question_id, user=user.id).order_by('-id')

    if not len(submissions):
        total_page = 1
    else:
        total_page = (len(submissions) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    filter_submissions = submissions[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['submissions'] = filter_submissions
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page
    return render(request, 'my_site/question_submissions.html', context)


@login_required
def show_question_submissions(request, question_id):

    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1

    context = dict()
    user = request.user
    question = get_object_or_404(MultipleChoice, pk=question_id)

    # Check authority
    # If user is administrator, show all submissions, or show submissions of the user
    if question_update_check(user, question):
        submissions = question.submission_set.all().order_by('-id')
    else:
        submissions = question.submission_set.filter(user=user.id).order_by('-id')

    if not len(submissions):
        total_page = 1
    else:
        total_page = (len(submissions) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    filter_submissions = submissions[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['submissions'] = filter_submissions
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page
    return render(request, 'my_site/question_submissions.html', context)


@login_required
def show_submissions(request):
    # Check the parameter, if page is invalid, page = 1
    try:
        page = int(request.GET['page'])
    except (ValueError, KeyError):
        page = 1

    context = dict()
    user = request.user
    questions = MultipleChoice.objects.all()
    filter_submissions = list()

    # Check authority
    # If user is administrator, show all submissions, or show submissions of the user
    if user.profile.authority > Authority.USER:
        for question in questions:
            if question_update_check(user, question):
                submissions = question.submission_set.all()
                filter_submissions += list(submissions)
            elif question_show_check(user, question):
                submissions = question.submission_set.filter(user=user.id)
                filter_submissions += list(submissions)
    else:
        for question in questions:
            if question_show_check(user, question):
                submissions = question.submission_set.filter(user=user.id)
                filter_submissions += list(submissions)

    filter_submissions = sorted(filter_submissions, key=lambda x: x.id, reverse=True)
    if not len(filter_submissions):
        total_page = 1
    else:
        total_page = (len(filter_submissions) - 1) // PAGE_MAX + 1
    pages, pre_page, next_page = get_pages(total_page, page)
    filter_submissions = filter_submissions[PAGE_MAX * (page - 1): PAGE_MAX * page]

    context['submissions'] = filter_submissions
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page

    return render(request, 'my_site/question_submissions.html', context)


@login_required
def show_submission(request, submission_id):
    context = dict()
    user = request.user
    submission = get_object_or_404(Submission, pk=submission_id)
    question = submission.question
    # If user is administrator of the question or user owns the submission, show the submission
    if question_update_check(user, question):
        context['admin'] = True
    elif submission.user != user:
        messages.error(request, '没有权限')
        return HttpResponseRedirect(reverse('index'))
    context['submission'] = submission
    return render(request, 'my_site/show_submission.html', context)


@login_required
def edit_submission(request, submission_id):
    if request.method == 'POST':
        try:
            grade = int(request.POST.get('grade'))
            if not (0 <= grade <= 100):
                raise ValueError
            submission = get_object_or_404(Submission, pk=submission_id)
            question = submission.question
            user = request.user
            if question_update_check(user, question):
                submission.grade = grade
                submission.save()
                messages.info(request, '保存成功')
        except (ValueError, KeyError):
            messages.error(request, '格式错误')
    return HttpResponseRedirect(reverse('show_submission', args=(submission_id,)))


@login_required
def show_category_rank(request, category_id):
    context = dict()
    user = request.user
    category = get_object_or_404(Category, pk=category_id)
    user_grade = defaultdict(lambda :0)
    if category_update_check(user, category):
        for question in category.questions.all():
            for submission in question.submission_set.all():
                submission_user = submission.user.username
                submission_grade = submission.grade
                user_grade[(submission_user, question.id)] = max(submission_grade, user_grade[(submission_user, question.id)])
    else:
        for question in category.questions.all():
            for submission in question.submission_set.filter(user=user.id):
                submission_user = submission.user.username
                submission_grade = submission.grade
                user_grade[(submission_user, question.id)] = max(submission_grade, user_grade[(submission_user, question.id)])
    grades = defaultdict(lambda :0)
    for (u, q), g in user_grade.items():
        grades[u] += g
    context['grades'] = sorted(grades.items(), key=lambda x:x[1], reverse=True)
    context['category'] = category
    return render(request, 'my_site/show_rank.html', context)


@login_required
def show_exam_rank(request, exam_id):
    context = dict()
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    user_grade = dict()
    if exam_update_check(user, exam):
        for submission in exam.examsubmission_set.all():
            question_id = submission.question_id
            user_name = submission.user.username
            submission_grade = submission.grade
            try:
                _ = user_grade[(user_name, question_id)]
            except KeyError:
                if exam.start_time <= submission.submitted_date <= exam.end_time:
                    user_grade[(user_name, question_id)] = submission_grade
    else:
        for submission in exam.examsubmission_set.filter(user=user.id):
            question_id = submission.question_id
            user_name = submission.user.username
            submission_grade = submission.grade
            try:
                _ = user_grade[(user_name, question_id)]
            except KeyError:
                if exam.start_time <= submission.submitted_date <= exam.end_time:
                    user_grade[(user_name, question_id)] = submission_grade
    grades = defaultdict(lambda: 0)
    for (u, q), g in user_grade.items():
        grades[u] += g
    context['grades'] = sorted(grades.items(), key=lambda x: x[1], reverse=True)
    context['exam'] = exam
    return render(request, 'my_site/show_rank.html', context)


@login_required
def generate_random_exam(request):
    user = request.user
    if request.method == 'POST' and exam_add_check(user):
        try:
            num_question = int(request.POST.get('count', '10'))
            grade = int(request.POST.get('grade', '1'))
        except ValueError:
            messages.error(request, '请正确填写数值')
            return HttpResponseRedirect(reverse('index'))
        question_ids = [str(q.id) for q in MultipleChoice.objects.all() if question_show_check(user, q)]
        random.shuffle(question_ids)
        question_ids = question_ids[:num_question + 1]
        grades = [grade] * num_question
        exam_form = ExamForm(request.POST)
        if not exam_form.is_valid():
            messages.error(request, '表单不合法')
            return HttpResponseRedirect(reverse('index'))
        exam = exam_form.save()
        exam.admins.add(user)
        for question_id, question_grade in zip(question_ids, grades):
            question = MultipleChoice.objects.get(pk=question_id)
            exam.questions.add(question)
            grade = Grade.objects.create(exam=exam, question=question, grade=question_grade)
            grade.save()
        exam.save()
        messages.info(request, '创建成功')
        return HttpResponseRedirect(reverse('exams'))


def test(request):
    return render(request, 'my_site/test.html')


def get_pages(total_page, cur_page):
    pages = [i + 1 for i in range(total_page)]
    if cur_page > 1:
        pre_page = cur_page - 1
    else:
        pre_page = 1
    if cur_page < total_page:
        next_page = cur_page + 1
    else:
        next_page = total_page
    if cur_page <= 2:
        pages = pages[:5]
    elif total_page - cur_page <= 2:
        pages = pages[-5:]
    else:
        pages = filter(lambda x: abs(x - cur_page) <= 2, pages)
    return pages, pre_page, next_page