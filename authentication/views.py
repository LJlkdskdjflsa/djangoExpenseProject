from django.core import mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from djangoExpenseProject.settings import EMAIL_HOST_USER

from django.contrib import auth
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import status
import json
from validate_email import validate_email
from .utils import AppTokenGenerator, account_activation_token


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

        # contain values of previous request (posted)
        context = {
            'field_values': request.POST
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
            # path to view
            # getting domain we are on
            # relative url to verification
            # encode uid
            # token
            # uidb64 = urlsafe_base64_encode(force_bytes(bytes(user.pk)))
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            # uidb64 = force_bytes(urlsafe_base64_encode(user.pk))

            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={
                'uidb64': uidb64,
                'token': account_activation_token.make_token(user)
            })

            activate_url = 'http://' + domain + link
            # email
            email_subject = 'Activate your email'
            email_body = 'Hi' + user.username + \
                         'Please use the link below to verify your account.\n' + \
                         activate_url
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

        # check regular expression
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

        # check regular expression
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


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not account_activation_token.check_token(user, token):
                return redirect('login')

            if user.is_active:
                return redirect('login')

            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            messages.success(request, 'Account activated failed')
            print(ex)
            return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:

            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username + ' you are logged in')
                    return redirect('expenses')

                messages.error(request, 'Account is not active, please check your email')
                return render(request, 'authentication/login.html')

            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')

        messages.error(request, 'please filled all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

