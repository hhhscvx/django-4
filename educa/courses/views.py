from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Course
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


class OwnerMixin:  # mixin owner`а
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)  # только те курсы, которые создал auth user (чтоб не трогал чужие)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user  # задает владельцем курса текущего пользователя
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,  # редачить курс только если авторизован
                       PermissionRequiredMixin):  # и с опред. правами
    model = Course  # модель
    fields = ['subject', 'title', 'slug', 'overview']  # поля для использования в форме, связанной с представлением
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'  # форма редактирования курса (CreateView, UpdateView)


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'  # отображение списка курсов пользователя
    permission_required = 'courses.view_course'  # имеются ли у user`а данные права


class CourseCreateView(OwnerCourseEditMixin, CreateView):  # создание нового объекта Course (по полям в fields)
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):  # редактирование объект Course по полям в fields
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'  # подтверждение об удалении курса
    permission_required = 'courses.delete_course'
