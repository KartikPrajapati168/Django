from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from cases.models import Case
from documents.models import Document

# Create your views here.
class DashboardView(APIView):
    def get(self,request):
        total_users=User.objects.count()
        total_cases=Case.objects.count()
        total_docs=Document.objects.count()

        return Response({
            'total_users':total_users,
            'total_cases':total_cases,
            'total_documents':total_docs,
        })