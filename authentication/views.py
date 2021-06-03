from django.core import mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from djangoExpenseProject.settings import EMAIL_HOST_USER

from django.contrib import auth
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status
import json
from validate_email import validate_email
from .utils import account_activation_token

import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


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

            current_site = get_current_site(request)
            link = reverse('activate', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user)
            })

            activate_url = 'http://' + current_site.domain + link
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
            EmailThread(email).start()
            #email.send(fail_silently=False)
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


class RequestPasswordSetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):

        context = {
            'field_values': request.POST
        }
        email = request.POST['email']

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset_password.html', context)

        exists = User.objects.filter(email=email).exists()
        if exists:
            user = User.objects.get(email=email)
            print((user.pk))
            print((user))

            # user = user_list[0]
            domain = get_current_site(request).domain
            link = reverse('set_new_password', kwargs={
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': PasswordResetTokenGenerator().make_token(user)
            })

            reset_password_url = 'http://' + domain + link
            # email
            email_subject = 'Password reset Instruction'
            email_body = 'Hi ' + user.username + \
                         ' \nPlease use the link below to reset your password.\n' + \
                         reset_password_url
            email = mail.EmailMessage(
                email_subject,
                email_body,
                EMAIL_HOST_USER,
                [email],
            )
            EmailThread(email).start()

            messages.success(request, 'We have send you an email,'
                                      'please use it to reset your password')
            return render(request, 'authentication/reset_password.html')

        else:
            messages.error(request, 'Sorry, we can\'t find this email')
            return render(request, 'authentication/reset_password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, "Password reset link is invalid, please get a new one.")
                return render(request, 'authentication/reset_password.html', context)
        except Exception as e:
            # trace exception
            # import pdb
            # pdb.set_trace()
            messages.info(request, "something went wrong, try again.")
            return render(request, 'authentication/reset_password.html', context)

        return render(request, 'authentication/set_new_password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']

        if password != confirm_password:
            messages.error(request, "Password didn't match.")
            return render(request, 'authentication/set_new_password.html', context)

        if len(password) < 6:
            messages.error(request, "Password is too short, must longer than 6 words.")
            return render(request, 'authentication/set_new_password.html', context)

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, "Password reset link is invalid, please get a new one.")
                return render(request, 'authentication/set_new_password.html', context)
            user.set_password(password)
            user.save()
            # verify is the link has been used before
            messages.success(request, "Password reset successfully, you can login with your new password")
            return redirect('login')
        except Exception as e:
            # trace exception
            # import pdb
            # pdb.set_trace()
            messages.info(request, "something went wrong, try again.")
            return render(request, 'authentication/set_new_password.html', context)
