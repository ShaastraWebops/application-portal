#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context import RequestContext
from django.shortcuts import render_to_response, redirect
from django.conf import settings
#from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory,inlineformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test

from account.models import *
from core.models import *
from coord.models import *
from coord.forms import *

@login_required
@user_passes_test(lambda u: not u.get_profile().is_core_of)
def coord_home(request):
    """
    Can edit profile,logout
    Sees list of sub-departments, submit application, set preference order etc.

    #TODO: Add is_coord decorator
    """
    profile = UserProfile.objects.get(user__id = request.user.id)
    try:
        apps = Application.objects.filter(user = request.user).exclude(preference = -1).order_by('preference')
    except:
        pass
    form = SelectSubDeptForm()
    if request.method == "POST":
        form = SelectSubDeptForm(request.POST)
        if form.is_valid():
            name = str(form.cleaned_data['name']).split('| ')
            subdept = SubDept.objects.get(name = str(name[1]).strip())
            names=['Hovercraft Making Workshop','Desmod','How Things Work', 'Gamedrome', 'Industrially Defined Problem Statement (IDP)','Shaastra Junior','Sustainable Cityscape', 'Project X']	
            #if subdept.name in names:
            return redirect('coord.views.application', sub_dept_id=subdept.id)
        else:
            print "Form in invalid"
    return render_to_response("coord/home.html", locals(),context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: not u.get_profile().is_core_of)
def application(request, sub_dept_id = None):
    """
    Displays questions of the sub-department with id = sub_dept_id

    #TODO: Do no accept form if an answer is blank
    """
    subdept = SubDept.objects.get(id = sub_dept_id)
    can_apply = False
    if subdept.first_yr_apps and request.user.username[2:5].lower().find("13b") != -1:
        can_apply = True
    if subdept.non_first_yr_apps and request.user.username[2:5].lower().find("13b") == -1:
        can_apply = True
    
    try:
        inst = Instructions.objects.get(sub_dept = subdept)
    except:
        pass
    qns = Question.objects.filter(subdept__id = sub_dept_id).order_by('id')
    number_of_questions = qns.count()
    #Create as many answer forms as there are questions
    try:
        AnswerFormSet = modelformset_factory(Answer, form = AnswerForm, extra = number_of_questions)
        a = Application.objects.get(user = request.user, subdept__id = sub_dept_id)
        data = {'preference':a.preference,'references':a.references,'credentials' : a.credentials,
                'subdept':subdept,'user':request.user,}
        if request.method == 'POST':
            #AnswerFormSet = modelformset_factory(Answer, form = AnswerForm)
            forms = AnswerFormSet(request.POST,queryset = a.answers.all())
            app = ApplicationForm(request.POST,data)
            #print forms
            if forms.is_valid() and app.is_valid():
                print "blah"
                forms = forms.save()
                print "saved"
                ref = Reference.objects.get(id = a.references.id)
                ref.content = app.cleaned_data['references']
                ref.save()
                cred = Credential.objects.get(id = a.credentials.id)
                cred.content = app.cleaned_data['credentials']
                cred.save()
                a.references = ref
                a.credentials = cred
                a.preference = app.cleaned_data['preference']
                a.save()
                msg = "You have successfully edited your application"
                return redirect('coord.views.coord_home')
        else:
            forms = AnswerFormSet(queryset = a.answers.all())
            app = ApplicationForm(initial = data)

    except:
        AnswerFormSet = modelformset_factory(Answer, form = AnswerForm, extra = number_of_questions)
        if request.method == 'POST':
            n = 0
            initial_list = []
            data = 'Enter answer here'
            while n != number_of_questions:
                initial_list.append({'answer':data})
                n = n+1
            forms = AnswerFormSet(request.POST,initial=initial_list)
            app = ApplicationForm(request.POST)
            if forms.is_valid() and app.is_valid():
                temp = app.save(commit = False)
                forms = forms.save(commit = False)
                ref = Reference(content = app.cleaned_data['references'])
                ref.save()
                cred = Credential(content = app.cleaned_data['credentials'])
                cred.save()
                temp.user = request.user
                temp.references = ref
                temp.credentials = cred
                temp.subdept = subdept
                temp.save()
                curr = Application.objects.get(id = temp.id)
                n = 0
                for f in forms:
                    f.question = qns[n]
                    n=n+1
                    f.save()
                    ans = Answer.objects.get(id = f.id)
                    curr.answers.add(ans)
                    comment = Comments(answer = ans, comment = " ")
                    comment.save()
                curr.save()
                appcomment = AppComments(app = curr, comment = " ")
                appcomment.save()
                msg = "You have successfully submitted your application"
                return redirect('coord.views.coord_home')
        else:
            forms = AnswerFormSet(queryset = Answer.objects.none())
            app = ApplicationForm(initial={'subdept':subdept,'user':request.user,})

    zipped = zip(qns,forms)
    return render_to_response("coord/application.html", locals(),context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: not u.get_profile().is_core_of)
def delete(request, sub_dept_id = None):
    subdept = SubDept.objects.get(id = sub_dept_id)
    app = Application.objects.get(user = request.user, subdept__id = sub_dept_id)
    app.preference = -1
    app.save()
    return redirect('coord.views.coord_home')
