from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'  # шаблон данного представления
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):  # при отправке валидных данных. переопределяем чтобы user`а сразу логинило
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'], password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm  # указываем форму которую будем обрабатывать

    def form_valid(self, form):
        self.course = form.cleaned_data['course']  # присваивает курс который пользователь выбрал и зачисляет его
        self.course.students.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail',  # при зачислении на курс перекидывает на его detail
                            args=[self.course.id])  # sucess url это перенаправление на курс по его id


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])  # фильтр курсов где auth.user в списке студентов


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()  # объект курса (DetailView)
        if 'module_id' in self.kwargs:  # если в запросе есть определенный модуль то передаться в контекст его
            context['module'] = course.modules.get(
                id=self.kwargs['module_id'])
        else:  # иначе передать в контекст первый модуль
            context['module'] = course.modules.all()[0]
        return context
