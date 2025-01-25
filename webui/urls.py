from django.conf import settings
from django.urls import include, path
from django.contrib import admin

#from wagtail.admin import urls as wagtailadmin_urls
#from wagtail.core import urls as wagtail_urls
#from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views

from discordlogin import views
from dashboard.views import dashboard, guilddash
from django.views.generic.base import RedirectView
from premium.views import premium
from home.views import home
from botadministration.views import botadministration, itemadministration, edititem, edituser, editbotuser

#disable adminlogin
#class AccessUser:
#    has_module_perms = has_perm = __getattr__ = lambda s,*a,**kw: True

#admin.site.has_permission = lambda r: setattr(r, 'user', AccessUser()) or True



urlpatterns = [
    #path('waarbenikbelandisditvooradmins/', admin.site.urls),
    #path('waarbenikbelandisditvooradmins/login/', RedirectView.as_view(url='/')),
    #path('admin/', include(wagtailadmin_urls)),
    #path('documents/', include(wagtaildocs_urls)),

    #path('search/', search_views.search, name='search'),

]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", home, name='home'),
    path('auth/user', views.getAuthenticatedUser, name='getAuthenticatedUser'),
    path('oauth2', views.home, name='oauth2'),
    path('oauth2/login', views.discordLogin, name='oauthLogin'),
    path('oauth2/logout', views.discordLogout, name='oauthLogout'),
    path('oauth2/login/redirect', views.discordLoginRedirect, name='discordLoginRedirect'),
    path('dash/', dashboard, name='dashboardload'),
    path('dash/<int:id>', guilddash, name='guilddash'),
    path('premium', premium, name='dashboardload'),
    path('administration/users/', botadministration, name='botadministration'),
    path('administration/', itemadministration, name='administration'),
    path('administration/edituser/<int:id>', edituser, name='edituser'),
    path('administration/editbotuser/<int:id>', editbotuser, name='editbotuser'),
    path('administration/edititem/<str:id>', edititem, name='edititem'),
    path('administration/additem', edititem, name='additem'),
#    path("", include(wagtail_urls))
    
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)), 
]
