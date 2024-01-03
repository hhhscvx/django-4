from rest_framework import generics
from courses.models import Subject, Course
from courses.api.serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from courses.api.permissions import IsEnrolled


class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDetailView(generics.RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


# class CourseEnrollView(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]  # только для auth.user`s
#
#     def post(self, request, pk, format=None):  # user отправляет post на поступление, извлекается курс и его зачисляют
#         course = get_object_or_404(Course, pk=pk)
#         course.students.add(request.user)
#         return Response({'enrolled': True})


class CourseViewSet(viewsets.ReadOnlyModelViewSet):  # read only
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True, methods=['post'],  # post и detail (действие только на одним объектом)
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()  # в queryset указали Course, get_object ссылается на объект Course данного запроса
        course.students.add(request.user)
        return Response({'enrolled': True})  # ответ об успехе

    @action(detail=True, methods=['get'],
            serializer_class=CourseWithContentsSerializer,  # прорисовка содержимого курса
            authentication_classes=[BasicAuthentication],
            permission_classes=[IsAuthenticated, IsEnrolled])  # доступ к содержимому получают только поступившие users
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
