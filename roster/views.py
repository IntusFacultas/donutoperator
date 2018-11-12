from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.db.models import Count
from roster.models import Shooting, Tag, Source
from roster.forms import ShootingModelForm
from django.http import QueryDict
import datetime
import json
# Create your views here.


def connect_sources_and_tags(shooting, data):
    """Adds all sources and tags within data to given Shooting

    {
        "sources": [string, string,...],
        "tags": [string, string,...]
    }

    Arguments:
    :param shooting: a Shooting Django ORM object
    :param data: a dictionary with an array of strings for sources, and array of strings
        for tags as described above

    Returns:
    Nothing
    """
    for source in data["sources"]:
        if Source.objects.filter(text=source, shooting=shooting).count() == 0:
            Source.objects.create(
                text=source,
                shooting=shooting
            )
    for tag in data["tags"]:
        if Tag.objects.filter(text=tag, shooting=shooting).count() == 0:
            Tag.objects.create(
                text=tag,
                shooting=shooting
            )


def create_html_errors(form):  # pragma: no cover
    """Creates an HTML string of the form's errors

    Arguments:
    :param form: an invalid Django form

    Returns:
    a string of the rrors concatenated together.
    """
    error_string = ""
    for key, error in form.errors.items():
        error_string += "{}: {}<br>".format(key, error)
    return error_string


class DeleteShootingView(LoginRequiredMixin, View):
    def post(self, request):
        data = request.POST.get("id")
        try:
            Shooting.objects.get(pk=data).delete()
            return HttpResponse(status=200)
        except Shooting.DoesNotExist as e:
            return HttpResponse(str(e), status=500, )


class EditShootingView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.POST.get("shooting"))
        data["date"] = data["date"].split("T")[0]
        if (isinstance(data["age"], str) and
                len(data["age"]) == 0) or data["age"] is None:
            data["age"] = -1
        else:
            data["age"] = int(data["age"])
            if data["age"] < 0:
                return HttpResponse(
                    "Please provide a positive number for the age", status=400)
        try:
            shooting = Shooting.objects.get(pk=int(data["id"]))
        except Shooting.DoesNotExist as e:
            return HttpResponse(str(e), status=500, )
        form = ShootingModelForm(data, instance=shooting)
        if form.is_valid():
            shooting = form.save()
            shooting.tags.all().delete()
            shooting.sources.all().delete()
            shooting.unfiltered_video_url = data["video_url"]
            shooting.save()
            connect_sources_and_tags(shooting, data)
            return HttpResponse(status=200)
        return HttpResponse(create_html_errors(form), status=400)


class SubmitShootingView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.POST.get("shooting"))
        data["date"] = data["date"].split("T")[0]
        if (isinstance(data["age"], str) and
                len(data["age"]) == 0) or data["age"] is None:
            data["age"] = -1
        else:
            data["age"] = int(data["age"])
            if data["age"] < 0:
                return HttpResponse(
                    "Please provide a positive number for the age", status=400)
        form = ShootingModelForm(data)
        if form.is_valid():
            shooting = form.save()
            shooting.unfiltered_video_url = data["video_url"]
            shooting.save()
            connect_sources_and_tags(shooting, data)
            return HttpResponse(shooting.id, status=200)
        return HttpResponse(create_html_errors(form), status=400)


class RosterListView(View):
    def get(self, request, date=datetime.datetime.now().year):
        display_date = datetime.datetime(int(date), 1, 1, 0, 0)
        shootings = Shooting.objects.filter(
            date__year=display_date.year).order_by('-date')
        distinct_tags = Tag.objects.values('text').annotate(
            text_count=Count('text')).values('text')
        return render(request, "roster/index.html", {
            "shootings": [obj.as_dict() for obj in shootings],
            "total": shootings.count(),
            "year": display_date.year,
            "states": Shooting.STATE_CHOICES,
            "races": Shooting.RACE_CHOICES,
            "genders": Shooting.GENDER_CHOICES,
            "all_tags": distinct_tags,

        })
