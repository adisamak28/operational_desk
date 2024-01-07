# from re import template
from re import template
from django.views.generic import View
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt


# Django Authentication controller
# calls login_request method from service
class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return

class AuthenticationController(View):

    template_name = 'authentication/login.html'
    form_class = AuthenticationForm

    def get(self, request):
        form = self.form_class()
        if isinstance(request.user, AnonymousUser):
            return render(request, self.template_name, context={'form': form})
        else:
            return redirect("/old_data_req/home")

    def post(self, request):
        try:
            form = AuthenticationForm(request=request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('/old_data_req/home')
                else:
                    return render(request=request,
                                  template_name="authentication/login.html",
                                  context={"form": form})
            else:
                return render(request=request,
                              template_name="authentication/login.html",
                              context={"form": form})

        except Exception as error:
            return HttpResponse({error}, status=400)


class HomeView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'authentication/home.html'

    def get(self, request):
        return Response({}, template_name=self.template_name)

class LogoutView(APIView):

    def get(self, request):
        logout(request)
        messages.info(request, "Logged out successfully!")
        return redirect("/old_data_req/login")

class AuthenticationAPI(APIView):

    authentication_classes = [
        CsrfExemptSessionAuthentication, BasicAuthentication]

    def post(self, request):
        if isinstance(request.user, AnonymousUser):
            return Response({"status": False})
        return Response({"status": True})


def error_403(request, exception):
    return render(request, 'authentication/403.html')
