from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import routers, serializers, viewsets
from uelc.main import views
from uelc.main.models import UserProfile
from uelc.main.views import (
    UELCPageView, UELCEditView, FacilitatorView, UELCAdminView,
    UELCAdminEditUserView, UELCAdminCreateUserView,
    UELCAdminHierarchyView, UELCAdminCreateCohortView,
    UELCAdminEditCohortView, UELCAdminCreateCaseView,
    UELCAdminDeleteUserView)
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")
redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (
    r'^accounts/logout/$',
    'django.contrib.auth.views.logout',
    {'next_page': redirect_after_logout})
if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (
        r'^accounts/logout/$',
        'djangowind.views.logout',
        {'next_page': redirect_after_logout})
    admin_logout_page = (r'^admin/logout/$',
                         'djangowind.views.logout',
                         {'next_page': redirect_after_logout})


# Serializers define the API representation.
class UserProfileSerializer(serializers.ModelSerializer):
    cohorts = serializers.Field()

    class Meta:
        model = UserProfile
        fields = ('profile_type', 'cohorts',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer(many=False)

    class Meta:
        model = User
        fields = ("url", "username", "email", "profile")


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


router = routers.DefaultRouter()
router.register(r'user', UserViewSet)

urlpatterns = patterns(
    '',
    logout_page,
    admin_logout_page,
    auth_urls,
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    (r'^registration/', include('registration.backends.default.urls')),
    (r'^$', views.IndexView.as_view()),
    (r'^admin/', include(admin.site.urls)),
    (r'^uelcadmin/hierarchy/', UELCAdminHierarchyView.as_view()),
    (r'^uelcadmin/createcohort/', UELCAdminCreateCohortView.as_view()),
    (r'^uelcadmin/createcase/', UELCAdminCreateCaseView.as_view()),
    (r'^uelcadmin/editcohort/', UELCAdminEditCohortView.as_view()),
    (r'^uelcadmin/createuser/', UELCAdminCreateUserView.as_view()),
    (r'^uelcadmin/edituser/', UELCAdminEditUserView.as_view()),
    (r'^uelcadmin/deleteuser/', UELCAdminDeleteUserView.as_view()),
    (r'^uelcadmin/', UELCAdminView.as_view()),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'infranil/', include('infranil.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^pagetree/', include('pagetree.urls')),
    (r'^quizblock/', include('quizblock.urls')),
    (r'^pages_save_edit/(?P<hierarchy_name>[-\w]+)/(?P<path>.*)$',
        'uelc.main.views.pages_save_edit'),
    (r'^pages/(?P<hierarchy_name>[-\w]+)/edit/(?P<path>.*)$',
     UELCEditView.as_view()),
    (r'^pages/(?P<hierarchy_name>[-\w]+)/instructor/(?P<path>.*)$',
     'uelc.main.views.instructor_page'),
    (r'^pages/(?P<hierarchy_name>[-\w]+)/facilitator/(?P<path>.*)$',
     FacilitatorView.as_view()),
    (r'^pages/(?P<hierarchy_name>[-\w]+)/(?P<path>.*)$',
     UELCPageView.as_view()),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
