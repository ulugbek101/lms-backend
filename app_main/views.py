from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from app_auth.models import Group, Room, Student


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
    now = timezone.localtime()
    weekday = timezone.localdate().weekday() + 1  # Monday = 1, ..., Sunday = 7

    todays_weekday = (
        "1-3-5"
        if weekday in range(1, 6, 2)
        else "2-4-6" if weekday in range(2, 7, 2) else ""
    )

    todays_lessons = Group.objects.select_related("teacher").all()

    # Time slots from 08:00 to 17:00
    time_slots = [f"{hour:02d}:00" for hour in range(8, 18)]

    schedule = {
        room.number: {slot: None for slot in time_slots} for room in Room.objects.all()
    }
    print(schedule.items())

    timetable_data = {
        room.number: {slot: None for slot in time_slots} for room in Room.objects.all()
    }

    for lesson in todays_lessons:
        start_hour = lesson.start_time.strftime("%H:00")
        end_hour = lesson.end_time.strftime("%H:00")
        print(start_hour, end_hour)

        if lesson.room.number not in timetable_data:
            timetable_data[lesson.room.number] = {}

        if lesson.room.number in schedule:
            for time_slot in time_slots:
                if start_hour <= time_slot < end_hour:
                    schedule[lesson.room.number][time_slot] = lesson.name

        for time_slot in time_slots:
            if start_hour <= time_slot < end_hour:
                student_count = Student.objects.filter(student_groups=lesson).count()
                timetable_data[lesson.room.number][time_slot] = {
                    "group_name": lesson.name,
                    "teacher_name": lesson.teacher.full_name,
                    "start_date": lesson.start_date.strftime("%Y-%m-%d"),
                    "end_date": lesson.end_date.strftime("%Y-%m-%d"),
                    "student_count": student_count,
                }

    context = {
        "analytics_page": True,
        "timetable": timetable_data,
        "hours": time_slots,
    }

    return render(request, "app_auth/analytics.html", context)


@login_required(login_url="login")
def subjects(request):
    context = {
        "subjects_page": True,
    }
    return render(request, "app_main/subjects.html", context)
