from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.views.decorators.http import require_http_methods
import json
from .models import Usuarios
from django.http.response import HttpResponse, JsonResponse
from rest_framework import status
from .security import Security
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


# @require_http_methods(["GET"])
# def userLogin(request):
#     userCredentials = json.loads(request.body)
#     userCode = userCredentials['user_code']
#     userPassword = userCredentials['user_password']
    
#     authenticatedUser = UserAuthentication.verifyUser({"idusuario":userCode, 
#                                                        "clave":userPassword})

#     if (authenticatedUser['STATUS'] == status.HTTP_302_FOUND):
#         encodedToken = Security.generateNewToken(authenticatedUser['content'][0])
#         return JsonResponse({'STATUS': status.HTTP_201_CREATED,
#                              'ACCESS_TOKEN': encodedToken['ACCESS_TOKEN'],
#                              'REFRESH_TOKEN': encodedToken['REFRESH_TOKEN']}, 
#                              content_type = "application/json")
#     else:
#         return JsonResponse({'STATUS':status.HTTP_204_NO_CONTENT}, 
#                             content_type = "application/json")


# class UserAuthentication():
#     @classmethod
#     def verifyUser(cls, userCredentials):
#         try:
#             authenticatedUser = None
#             dataBaseUsers = list(Usuarios.objects.values('idusuario', 'clave'))
#             print(dataBaseUsers)
#             for i in range(len(dataBaseUsers)):
#                 if (dataBaseUsers[i] == userCredentials):
#                     _user = list(Usuarios.objects.filter(idusuario=userCredentials['idusuario']).values())
#                     authenticatedUser = _user
#                     print(authenticatedUser)
#                     requestStatus = status.HTTP_302_FOUND
#                     break
#                 else:
#                     authenticatedUser = False
#                     requestStatus = status.HTTP_404_NOT_FOUND
            
#             response = {'STATUS':requestStatus, 'content':authenticatedUser}
#             return response
           
#         except:
#             print("Holi")


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_code'] = user.username
        token['user_name'] = f"{user.first_name} {user.last_name}"
        token['user_privileges'] = [user.is_staff, user.is_superuser]

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class HomeView(APIView):
     
    permission_classes = (IsAuthenticated, )
    def get(self, request):
        content = {'message': 'Welcome to the JWT Authentication page using React Js and Django!'}
        print(request.body)
        return Response(content)
    

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
          
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)