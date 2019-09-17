from django.contrib.auth import login as auth_login
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import LoginSerializer
from users.api.serializers import UserSerializer


@method_decorator(sensitive_post_parameters('password'), name='dispatch')
class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = LoginSerializer
    www_authenticate_realm = 'api'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_login(self.request, serializer.user)
        return Response(UserSerializer(serializer.user).data)
