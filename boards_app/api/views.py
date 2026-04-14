from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class BoardListView(APIView):
    pass

class BoardDetailView(APIView):
    pass