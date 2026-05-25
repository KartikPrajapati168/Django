from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny          # <-- import this
from .models import ContactMessage
from .serializers import ContactMessageSerializer

class ContactView(APIView):
    permission_classes = [AllowAny]                       # <-- add this line

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Message sent successfully!"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Optional: you may want to restrict GET to admins only
        # but for simplicity leave it open or add custom permission
        messages = ContactMessage.objects.all()
        serializer = ContactMessageSerializer(messages, many=True)
        return Response(serializer.data)