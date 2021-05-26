from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User

from rest_framework import status
import json
from validate_email import validate_email

# register
class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        #check regular expression
        if not str(username).isalnum():
            return JsonResponse(
                {'username_error':
                 'username should contain only alphanumeric characters'
                 }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {'username_error':
                 'sorry, the username has been used, please choose another one'
                 }, status=status.HTTP_409_CONFLICT)

        return JsonResponse(
            {'username_valid': True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        #check regular expression
        if not validate_email(email):
            return JsonResponse(
                {'email_error':
                 'Email is invalid'
                 }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'email_error':
                 'sorry, the email has been used, please choose another one'
                 }, status=status.HTTP_409_CONFLICT)

        return JsonResponse(
            {'email_valid': True})

