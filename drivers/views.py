from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from . import constants, utils, models


# Create your views here.
@login_required
def drive(request):
    if request.user.username != constants.SUPERUSER_NAME:
        return Http404()
    if not len(models.Movie.objects.all()):
        utils.init_movie(constants.URLS)

    context = dict()
    movies = models.Movie.objects.all().order_by('-date')
    try:
        page = int(request.GET['page'])
    except (KeyError, ValueError):
        page = 1
    if not len(movies):
        total_page = 1
    else:
        total_page = (len(movies) - 1) // constants.PAGE_MAX + 1
    pages, pre_page, next_page = utils.get_pages(total_page, page)
    movies = movies[constants.PAGE_MAX * (page - 1): constants.PAGE_MAX * page]

    context['movies'] = movies
    context['page'] = page
    context['pages'] = pages
    context['pre_page'] = pre_page
    context['next_page'] = next_page
    return render(request, 'drivers/drive.html', context)