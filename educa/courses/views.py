from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Course
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from .forms import ModuleFormSet
from django.views.generic.base import TemplateResponseMixin, View
from .models import Module, Content
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin


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


class CourseModuleUpdateView(TemplateResponseMixin,  # прорисовка шаблона и возврат http-ответа.
                             View):  # то что CourseModuleUpdateView - представление
    template_name = 'courses/manage/module/formset.html'  # шаблон с формой
    course = None

    def get_formset(self, data=None):  # возвращение формсета (передаем наш из forms)
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):  # отправка
        self.course = get_object_or_404(Course,  # извлекаем course -> используем его в post и get
                                        id=pk,
                                        owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):  # get-запрос
        formset = self.get_formset()
        return self.render_to_response({  # context
            'course': self.course,
            'formset': formset})

    def post(self, request, *args, **kwargs):  # post-запрос
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')  # "mine/" name='manage_course_list'
        return self.render_to_response({'course': self.course, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'  # форма для создания и редактирования контента

    def get_model(self, model_name):  # получаем модель контента (text/video/image или file)
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',  # сама форма исключая некоторые поля
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):  # вызывается при получении запроса
        self.module = get_object_or_404(Module,  # модуль по id из запроса и если auth.user == course.owner
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)  # устанавливает модель вызываю модель по имени модели)
        if id:
            self.obj = get_object_or_404(self.model,  # объект текущей модели по id и auth.user == obj.owner
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)  # ну и эта хрень потому что так надо

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:  # id не указан значит создать новый объект
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):  # отправка post-запроса
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)  # контент прин. модулю который прин. курсу который прин. auth.user`у
        module = content.module  # модуль контента
        content.item.delete()  # удаление связанного с контентом объекта (text/file/video/image)
        content.delete()  # удаляется и сам контент
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):  # get-запрос
        module = get_object_or_404(Module,
                                   id=module_id,
                                   # в модели Module есть ForeignKey с course, поэтому мы можем обращаться к course
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):  # обработка csrf и json-ответов
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                  course__owner=request.user).update(order=order)  # обновляется порядок модулей
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)  # update content order
        return self.render_json_response({'saved': 'OK'})
