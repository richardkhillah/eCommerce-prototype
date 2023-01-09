import requests

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

from cart.views import _cart_id, _add_user_to_cart, _update_carts

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
                user = Account.objects.create_user(
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
            except IntegrityError as ie:
                messages.error(request, ie)
            return redirect('/accounts/login/?command=verification&email='+email)
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
            # if the user was shopping prior to loggin in, capture the cart used prior to
            # logging in and transfer the cart to the logged in user.
            anon_cart_id = _cart_id(request)
            auth.login(request, user)
            _update_carts(request, anon_cart_id)

            messages.success(request, 'You are logged in.')

            # Redirect to the 
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    # return redirect(params['next'])
                    return redirect('dashboard')
            except:
                pass
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
    # Cache user in cart so user can continue shopping on next login.
    _add_user_to_cart(request)

    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            
            # Send reset token
            current_site = get_current_site(request)
            mail_subject = 'Please Reset Your Password'
            message = render_to_string('passowrd_reset_email.html', {
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

            # Alert the user
            messages.success(request, "Password reset email has been set.")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist!")
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')

def reset_password_validate(request, uidb64, token):
    # Decode and validate password reset token
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist) as e:
        user = None
    
    # If decode and check successful, allow user to reset password
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')

    messages.error(request, 'Invalid activation link.')
    return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password == password_confirm:
            # get uid and user then set password, save, and redirect
            uid = request.session['uid']
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'Your password was successfully reset!')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')
    return render(request, 'reset_password.html')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')