#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.context import Context, RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from account.models import Announcement
from account.forms import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from recaptcha.client import captcha

def login(request):
    """
        View for handling login of users and redirecting to the respective dashboards on successful login.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active and not user.is_superuser:
            auth_login(request, user)
            nextURL = request.GET.get('next','')
            if nextURL != '':
                nextURL = nextURL[1:]  # For removing the leading slash from in front of the next parameter
                redirectURL = settings.SITE_URL + nextURL
                return HttpResponseRedirect(redirectURL)
            if user.get_profile().is_core_of:
                return HttpResponseRedirect(settings.SITE_URL + 'core/')
            else:
                return HttpResponseRedirect(settings.SITE_URL + 'coord/')
        invalid_login = True
        login_form = LoginForm()
        return render_to_response('index.html', locals(), context_instance=RequestContext(request))
    else:
        if request.user.is_authenticated():
            if request.user.get_profile().is_core_of:
                return HttpResponseRedirect(settings.SITE_URL + 'core/')
            else:
                return HttpResponseRedirect(settings.SITE_URL + 'coord/')        
        else:
            login_form = LoginForm()
        return render_to_response('login.html', locals(), context_instance=RequestContext(request))

def register(request):
    """
        View for handling Registration of new users after checking for reCAPTCHA.
    """
    if request.method == 'POST':
        register_form = RegistrationForm(request.POST)
        captcha_response = ''  # Added so that nothing gets displayed in the template if this variable is not set
        response = "random"
        # talk to the reCAPTCHA service
        """        
        response = captcha.submit(\
         request.POST.get('recaptcha_challenge_field'),
            request.POST.get('recaptcha_response_field'),  
            settings.RECAPTCHA_PRIVATE_KEY,  
            'shaastra.org',)  
        #     request.META['REMOTE_ADDR'],)  
        """
        if response:
            if register_form.is_valid():
                data = register_form.cleaned_data
                new_user = User(first_name = data['first_name'],
                                last_name  = data['last_name'],
                                username   = data['rollno'],
                                email      = data['email'])
                new_user.set_password(data['password'])
                new_user.is_active = True
                new_user.save()
                new_profile = UserProfile(user    = new_user,
                                          nick    = data['nick'],
                                          room_no = data['room_no'],
                                          hostel  = data['hostel'],
                                          cgpa    = data['cgpa'],
                                          ph_no   = data['ph_no'],)
                new_profile.save()
                registered = True
        else:
            captcha_response = response.error_code
    else:
        captcha_response = ''  # Added so that nothing gets displayed in the template if this variable is not set
        register_form = RegistrationForm()
    return render_to_response('register.html', locals(), context_instance=RequestContext(request))


def logout(request):
    """
        View for logging out users from the session.
    """
    if request.user.is_authenticated():
        auth_logout(request)
        return HttpResponseRedirect(settings.SITE_URL)
    else:
      return HttpResponseRedirect('/')

def editprofile(request):
    """
        View for editting the profile details of the currently logged in user.
    """
    user = request.user
    user_profile = user.get_profile()
    if request.method == 'POST':
        edit_form = EditUserProfileForm(request.POST, instance = user_profile)
        if edit_form.is_valid():
            edit_form.save()
            user.first_name = edit_form.cleaned_data['first_name']
            user.last_name  = edit_form.cleaned_data['last_name']
            user.save()
            editted = True
    else:
        values = {'first_name': user.first_name,
                  'last_name' : user.last_name,}
        edit_form = EditUserProfileForm(instance = user_profile, initial = values)
    return render_to_response('editprofile.html', locals(), context_instance=RequestContext(request))

