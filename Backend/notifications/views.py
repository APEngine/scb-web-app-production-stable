from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework import status


class NotificationList(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)
    
class NotificationCreate(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
class NotificationReadUpdate(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def partial_update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = True
        notification.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class NotificationDelete(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer