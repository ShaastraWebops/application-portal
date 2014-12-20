#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('account.urls')),
    url(r'^core/', include('core.urls')),
    url(r'^coord/', include('coord.urls')),
    url(r'^$', 'application_portal.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name':'password/reset.html', 'extra_context':{'site_name':'shaastra.org',}}, name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done',{'template_name':'password/reset_done.html', 'extra_context':{'site_name':'shaastra.org',}}, name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name':'password/reset_new_password.html', 'extra_context':{'site_name':'shaastra.org',}},
        name='password_reset_confirm'),

    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',{'template_name':'password/reset_complete.html', 'extra_context':{'site_name':'shaastra.org',}}, name='password_reset_complete'),

)

urlpatterns += patterns('django.views.static', (r'^static/(?P<path>.*)$'
                        , 'serve',
                        {'document_root': settings.STATIC_ROOT,
                        'show_indexes': True}))
