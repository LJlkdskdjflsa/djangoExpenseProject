from django.core import mail
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from djangoExpenseProject.settings import EMAIL_HOST_USER

from rest_framework import status
import json
from validate_email import validate_email

# register
class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # get user data
        # validate
        # create a user acount
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        #contain values of previous request (posted)
        context = {
            'field_values' : request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password) < 6:
                    messages.error(request, 'Password is too short, please try again')
                    return render(request, 'authentication/register.html', context)

            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = False

            user.save()

            # email
            email_subject = 'Activate your email'
            email_body = 'Test body'
            email = mail.EmailMessage(
                    email_subject,
                    email_body,
                    EMAIL_HOST_USER,
                    [email],
                )
            email.send(fail_silently=False)
            # fail_silently = False (get the error message)

            messages.success(request, 'Account successfully created')
            return render(request, 'authentication/register.html')

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

