from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import RegistrationForm
from .models import Account

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            try:
                user = Account(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        username=username,
                        password=password
                )
                user.phone_number = phone_number
                user.save()

                # User Activation
                current_site = get_current_site(request)
                mail_subject = 'Please activate your account'
                message = render_to_string('account_verification_email.html', {
                    'user': user,
                    'domain': current_site,
                    # Force encoding user id so primary key can not be seen.
                    # Will be decoded during account activation.
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(subject=mail_subject, body=message, to=[to_email])
                send_email.send()
                messages.success(request, "Registration successful.")
            except IntegrityError as ie:
                messages.error(request, ie)
            return redirect('register')
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'register.html', context=context)

from django.http import HttpResponse
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist) as e:
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated!')
        return redirect('login')
    messages.error(request, 'Invalid activation link.')
    return redirect('register')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            # messages.success(request, 'You are logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')