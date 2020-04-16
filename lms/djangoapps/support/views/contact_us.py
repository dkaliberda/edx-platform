"""
Signle support contact view
"""


from django.conf import settings
from django.http import Http404
from django.views.generic import View

from edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.features.enterprise_support import api as enterprise_api
from student.models import CourseEnrollment


class ContactUsView(View):
    """
    View for viewing and submitting contact us form.
    """

    def get(self, request):
        if not configuration_helpers.get_value('CONTACT_US_PAGE', True):
            raise Http404

        context = {
            'platform_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
            'support_email': configuration_helpers.get_value('CONTACT_EMAIL', settings.CONTACT_EMAIL),
            'custom_fields': settings.ZENDESK_CUSTOM_FIELDS
        }

        # Tag all issues with LMS to distinguish channel which received the request
        tags = ['LMS']

        # Per edX support, we would like to be able to route feedback items by site via tagging
        current_site_name = configuration_helpers.get_value("SITE_NAME")
        if current_site_name:
            current_site_name = current_site_name.replace(".", "_")
            tags.append("site_name_{site}".format(site=current_site_name))

        if request.user.is_authenticated:
            context['course_id'] = request.session.get('course_id', '')
            context['user_enrollments'] = CourseEnrollment.enrollments_for_user_with_overviews_preload(request.user)
            enterprise_customer = enterprise_api.enterprise_customer_for_request(request)
            if enterprise_customer:
                tags.append('enterprise_learner')

        context['tags'] = tags
        

        return render_to_response("support/contact_us.html", context)
