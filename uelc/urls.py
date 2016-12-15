import django.contrib.auth.views
import djangowind.views
import os.path
import uelc.main.helper_functions

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from uelc.main import views
from uelc.main.views import (
    UELCPageView, UELCEditView, FacilitatorView, UELCAdminView,
    UELCAdminCohortView, UELCAdminCreateHierarchyView,
    UELCAdminDeleteHierarchyView, UELCAdminUserView, UELCAdminCaseView,
    UELCAdminEditUserView, UELCAdminCreateUserView, UELCAdminEditUserPassView,
    UELCAdminEditCaseView, UELCAdminCreateCohortView, UELCAdminEditCohortView,
    UELCAdminDeleteCohortView, UELCAdminDeleteCaseView,
    UELCAdminCreateCaseView, UELCAdminDeleteUserView,
    AddCaseAnswerToQuestionView, EditCaseAnswerView, DeleteCaseAnswerView,
    SubmitSectionView, CloneHierarchyWithCasesView
)
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")
redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
logout_page = url(r'^accounts/logout/$', django.contrib.auth.views.logout,
                  {'next_page': redirect_after_logout})
if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))
    logout_page = url(r'^accounts/logout/$', djangowind.views.logout,
                      {'next_page': redirect_after_logout})
    admin_logout_page = url(r'^admin/logout/$', djangowind.views.logout,
                            {'next_page': redirect_after_logout})


urlpatterns = [
    logout_page,
    admin_logout_page,
    auth_urls,
    url(r'^registration/', include('registration.backends.default.urls')),
    url(r'^$', views.IndexView.as_view()),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^uelcadmin/case/', UELCAdminCaseView.as_view()),
    url(r'^uelcadmin/createhierarchy/',
        UELCAdminCreateHierarchyView.as_view()),
    url(r'^uelcadmin/cohort/(?P<pk>\d+)/', UELCAdminEditCohortView.as_view(),
        name='uelcadmin-edit-cohort'),
    url(r'^uelcadmin/cohort/', UELCAdminCohortView.as_view(),
        name='uelcadmin-view-cohort'),
    url(r'^uelcadmin/user/(?P<pk>\d+)/', UELCAdminEditUserView.as_view(),
        name='uelcadmin-edit-user'),
    url(r'^uelcadmin/user/', UELCAdminUserView.as_view(),
        name='uelcadmin-user-view'),
    url(r'^uelcadmin/createcohort/', UELCAdminCreateCohortView.as_view()),
    url(r'^uelcadmin/createcase/', UELCAdminCreateCaseView.as_view()),
    url(r'^uelcadmin/deletehierarchy/',
        UELCAdminDeleteHierarchyView.as_view()),
    url(r'^uelcadmin/editcase/', UELCAdminEditCaseView.as_view()),
    url(r'^uelcadmin/deletecase/', UELCAdminDeleteCaseView.as_view()),
    url(r'^uelcadmin/deletecohort/', UELCAdminDeleteCohortView.as_view()),
    url(r'^uelcadmin/createuser/', UELCAdminCreateUserView.as_view()),
    url(r'^uelcadmin/edituserpass/(?P<pk>\d+)/$',
        UELCAdminEditUserPassView.as_view(), name='uelcadmin_edituserpass'),
    url(r'^uelcadmin/deleteuser/', UELCAdminDeleteUserView.as_view()),
    url(r'^uelcadmin/', UELCAdminView.as_view(), name='uelcadmin'),
    url(r'^edit_question/(?P<pk>\d+)/add_case_answer/$',
        AddCaseAnswerToQuestionView.as_view(), {},
        'add-case-answer-to-question'),
    url(r'^edit_question/(?P<pk>\d+)/delete_case_answer/$',
        DeleteCaseAnswerView.as_view(), {},
        'delete-case-answer'),
    url(r'^edit_case_answer/(?P<pk>\d+)/$', EditCaseAnswerView.as_view(), {},
        'edit-case-answer'),
    url(r'^_impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'infranil/', include('infranil.urls')),
    url(r'^uploads/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^pagetree/clone_hierarchy/(?P<hierarchy_id>\d+)/$',
        CloneHierarchyWithCasesView.as_view(), name='clone-hierarchy'),
    url(r'^pagetree/', include('pagetree.urls')),
    url(r'^quizblock/', include('quizblock.urls')),
    url(r'^pages_save_edit/(?P<hierarchy_name>[-\w]+)/(?P<path>.*)$',
        uelc.main.helper_functions.pages_save_edit),
    url(r'^pages/(?P<hierarchy_name>[-\w]+)/edit/(?P<path>.*)$',
        UELCEditView.as_view()),
    url(r'^submit_section/', SubmitSectionView.as_view()),
    url(r'^pages/(?P<hierarchy_name>[-\w]+)/instructor/(?P<path>.*)$',
        uelc.main.helper_functions.instructor_page),
    url(r'^facilitator/fresh_token/$', uelc.main.helper_functions.fresh_token),
    url(r'^group_user/fresh_token/(?P<section_id>\d+)/$',
        uelc.main.helper_functions.fresh_grp_token),
    url(r'^pages/(?P<hierarchy_name>[-\w]+)/facilitator/(?P<path>.*)$',
        FacilitatorView.as_view(), name='facilitator-view'),
    url(r'^pages/(?P<hierarchy_name>[-\w]+)/(?P<path>.*)$',
        UELCPageView.as_view()),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
