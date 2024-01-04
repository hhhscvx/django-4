from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from courses.models import Course


@login_required
def course_chat_room(request, course_id):
    try:
        course = request.user.course_joined.get(id=course_id)
        return render(request, 'chat/room.html', {'course': course})
    except Course.DoesNotExist:
        return HttpResponseForbidden("Вы не присоединены к этому курсу.")
    return render(request, 'chat/room.html', {'course': course})
