from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from bodycams.models import Bodycam
from django.urls import reverse
from django.contrib import messages
from roster.models import Shooting, Tag
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import json
from django.views import View
from bodycams.forms import BodycamModelForm
# Create your views here.


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


class BodycamLink(LoginRequiredMixin, View):
	def post(self, request):
		"""AJAX only
		Links an existing bodycam and an existing killing together based on id

		Expects:
		bodycam_id: integer id of an existing bodycam,
		shooting_id: integer id of an existing killing,

		Arguments:
		:param request: a Django WSGI request object with the data described above

		Returns:
		on success - HTTP Status 200,
		on error - HTTP Status 500,  exception string
		"""
		bodycam_id = int(request.POST.get("bodycam_id"))
		shooting_id = int(request.POST.get("shooting_id"))
		try:
			bodycam = Bodycam.objects.get(pk=bodycam_id)
			shooting = Shooting.objects.get(pk=shooting_id)
		except (Bodycam.DoesNotExist, Shooting.DoesNotExist) as e:
			return HttpResponse(str(e), status=500, )
		bodycam.shooting = shooting
		bodycam.save()
		return HttpResponse(status=200)


class BodycamEdit(LoginRequiredMixin, View):
	def post(self, request):
		"""AJAX only
		Edits an existing bodycam, including tags, then returns the id of the
		bodycam to the client

		Expects:
		a stringified bodycam JSON object in the following format:
		bodycam: {
						id: integer,
						title: string,
						video: string iframe embed code with a width and height specified,
						description: string,
						department: string,
						state: string,
						city: string,
						date: string: "YYYY-MM-DDTH:mm:ss",
						tags: [],
						shooting: integer (pk),
		},
		Arguments:
		:param request: a Django WSGI request object with the data described above

		Returns:
		on success - HTTP Status 200, created bodycam id
		on error - HTTP Status 400,  form errors as HTML
		"""
		data = json.loads(request.POST.get("bodycam"))
		id = data["id"]
		try:
			bodycam = Bodycam.objects.get(pk=id)
		except Bodycam.DoesNotExist:
			return HttpResponse(
				"We couldn't find that bodycam in our database anymore.", status=400)
		data["date"] = data["date"].split("T")[0]
		form = BodycamModelForm(data, instance=bodycam)
		if form.is_valid():
			bodycam = form.save()
			bodycam.tags.all().delete()
			for tag in data["tags"]:
				Tag.objects.create(
					text=tag,
					bodycam=bodycam
				)
			return HttpResponse(bodycam.id, status=200)
		return HttpResponse(create_html_errors(form), status=400)


class BodycamSubmit(LoginRequiredMixin, View):
	def post(self, request):
		'''AJAX only
		Creates a new bodycam, with tags added to it, and then returns the id of the
		bodycam to the client

		Expects:
		A stringified bodycam JSON object in the following format:
		bodycam: {
						id: integer,
						title: string,
						video: string iframe embed code with a width and height specified,
						description: string,
						department: string,
						state: string,
						city: string,
						date: string: "YYYY-MM-DDTH:mm:ss",
						tags: [],
						shooting: integer (pk),
		},

		Arguments:
		:param request: a Django WSGI request object with the data described above

		Returns:
		on success - HTTP Status 200, created bodycam id
		on error - HTTP Status 400,  form errors as HTML
		'''
		data = json.loads(request.POST.get("bodycam"))
		data["date"] = data["date"].split("T")[0]
		form = BodycamModelForm(data)
		if form.is_valid():
			bodycam = form.save()
			for tag in data["tags"]:
				Tag.objects.create(
					text=tag,
					bodycam=bodycam
				)
			if data["shooting"] != "" and data["shooting"] is not None:
				try:
					shooting = Shooting.objects.get(pk=int(data["shooting"]))
				except Exception as e:
					return HttpResponse("We've created the bodycam but when we tried to link the bodycam to the shooting you requested, we couldn't find the shooting. Please refresh the page and try to link the bodycam manually.", status=406)
				bodycam.shooting = shooting
				bodycam.save()
			return HttpResponse(bodycam.id, status=200)
		return HttpResponse(create_html_errors(form), status=400)


class BodycamDashboard(LoginRequiredMixin, View):
	def get(self, request, date=datetime.datetime.now().year):
		display_date = datetime.datetime(int(date), 1, 1, 0, 0)
		distinct_tags = Tag.objects.values('text').annotate(
			text_count=Count('text')).values('text')
		return render(request, "bodycam/bodycam_dashboard.html", {
			"bodycams": [obj.as_dict() for obj in Bodycam.objects.all().order_by("-date")],
			"year": display_date.year,
			"states": Shooting.STATE_CHOICES,
			"races": Shooting.RACE_CHOICES,
			"genders": Shooting.GENDER_CHOICES,
			"all_tags": distinct_tags,
		})

	def post(self, request):
		pk = request.POST.get("pk")
		try:
			article = Bodycam.objects.get(pk=pk)
			article.delete()
			messages.success(request, "Article deleted successfully")
			return HttpResponseRedirect(reverse("bodycam:dashboard"))
		except Bodycam.DoesNotExist:
			messages.error(request, "We couldn't find that article in the database.")
			return HttpResponseRedirect(reverse("blog:dashboard"))


class BodycamIndexView(View):
	def get(self, request, date=datetime.datetime.now().year):
		'''Returns the bodycam index view

		Arguments:
		:param request: a Django WSGI request object with the data described above
		:param date: an optional parameter that defaults to the current year if not
		provided

		Returns:
		a render of the bodycams, the number of bodycams, the year, and the departments
		on error - HTTP Status 400,  form errors as HTML
		'''
		display_date = datetime.datetime(int(date), 1, 1, 0, 0)
		bodycams = Bodycam.objects.filter(
			date__year=display_date.year).order_by("-date")
		return render(request, "bodycam/bodycam_index.html", {
			"bodycams": [obj.as_dict() for obj in bodycams],
			"total": bodycams.count(),
			"year": display_date.year,
			"departments": bodycams.order_by("department").values('department'),
		})
