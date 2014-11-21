from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import routers, serializers, viewsets
from pagetree.generic.views import EditView, InstructorView
from uelc.main import views
from uelc.main.models import UserProfile
from uelc.main.views import UELCPageView
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


# Serializers define the API representation.
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('profile_type',)


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
    auth_urls,
    logout_page,
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    (r'^registration/', include('registration.backends.default.urls')),
    (r'^$', views.IndexView.as_view()),
    (r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'infranil/', include('infranil.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^pagetree/', include('pagetree.urls')),
    (r'^quizblock/', include('quizblock.urls')),
    (r'^pages/edit/(?P<path>.*)$', login_required(EditView.as_view(
        hierarchy_name="main",
        hierarchy_base="/pages/")),
     {}, 'edit-page'),
    (r'^pages/instructor/(?P<path>.*)$',
        login_required(InstructorView.as_view(
            hierarchy_name="main",
            hierarchy_base="/pages/"))),
    (r'^pages/(?P<path>.*)$', UELCPageView.as_view(
        hierarchy_name="main",
        hierarchy_base="/pages/")),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
