import json
import uuid

from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from app_auth.models import Group, Room, Subject
from app_auth.serializers import SubjectSerializer


@login_required(login_url="login")
def analytics(request):
    """
    Display the analytics page with a timetable of today's group lessons.

    The function determines today's weekday type (1-3-5 or 2-4-6) and
    generates a schedule from 08:00 to 17:00, mapping lesson times to rooms.

    **Context:**
    - `analytics_page`: Boolean flag to indicate the analytics page is active.
    - `timetable`: A dictionary representing the room-wise lesson schedule.
    - `hours`: A list of time slots from 08:00 to 17:00.

    **Template:**
    - `app_auth/analytics.html`
    """
    # now = timezone.localtime()
    weekday = timezone.localdate().weekday() + 1  # Monday = 1, ..., Sunday = 7

    todays_weekday = "1-3-5" if weekday in range(
        1, 6, 2) else "2-4-6" if weekday in range(2, 7, 2) else ""

    todays_lessons = Group.objects.filter(lesson_days=todays_weekday)

    # Time slots from 08:00 to 17:00
    time_slots = [f"{hour:02d}:00" for hour in range(8, 18)]

    schedule = {
        room.number: {slot: None for slot in time_slots} for room in Room.objects.all()
    }

    for lesson in todays_lessons:
        start_hour = lesson.start_time.strftime("%H:00")
        end_hour = lesson.end_time.strftime("%H:00")

        if lesson.room.number in schedule:
            for time_slot in time_slots:
                if start_hour <= time_slot < end_hour:
                    schedule[lesson.room.number][time_slot] = lesson.name

    context = {
        "analytics_page": True,
        "timetable": schedule,
        "hours": time_slots,
    }
    return render(request, "app_auth/analytics.html", context)


# @login_required(login_url="login")
# def subjects(request):
#     context = {
#         "subjects_page": True,
#         "subjects": Subject.objects.all(),
#     }
#     return render(request, "app_main/subjects.html", context)

class SubjectsView(LoginRequiredMixin, ListView):
    queryset = Subject.objects.all()
    context_object_name = "subjects"
    login_url = reverse_lazy("login")
    template_name = "app_main/subjects.html"
    paginator_class = Paginator
    paginate_by = 2

    extra_context = {
        "subjects_page": True,
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["subjects_data"] = SubjectSerializer(self.queryset, many=True).data
        return context



