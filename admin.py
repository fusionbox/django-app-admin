from django.utils.translation import ugettext as _
from django import http
from django.template.response import TemplateResponse
from django.template.loader import get_template, find_template
from django.template.base import TemplateDoesNotExist
from django.template import RequestContext
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache


from django.contrib import admin
from django.contrib.admin.sites import AdminSite


class AppAdminSite(AdminSite):
    _registered_apps = {}

    def register_app(self, app_name, app_admin_class):
        if app_name not in self._registered_apps:
            self._registered_apps[app_name] = app_admin_class(app_admin_site=self)
        return self._registered_apps[app_name]

    @never_cache
    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        if extra_context is None:
            extra_context = {}
        apps = {}
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label

            apps[app_label] = self.bucket_for_app(request, app_label, extra_context)

        app_list = apps.items()  # tuple of key, value
        app_list.sort(key=lambda x: x[0])  # sorted by key
        app_list = [v[1] for v in app_list]  # extract values only

        context = extra_context or {}
        context.update({
            'title': _('Site administration'),
            'apps': app_list,
        })
        return TemplateResponse(request, self.index_template or [
            'admin/appadmin/index.html',
        ], context, current_app=self.name)

    @never_cache
    def app_index(self, request, app_label, extra_context=None):
        if extra_context is None:
            extra_context = {}

        context = {
            'title': _('%s administration') % capfirst(app_label),
        }
        context.update(extra_context)

        app_dict = self._get_app_dict(request, app_label, extra_context)
        if not app_dict:
            raise http.Http404('The requested admin page does not exist.')

        # add content from ModelAdmin and/or AppAdmin
        if app_label in self._registered_apps:
            app_dict.update(self._registered_apps[app_label].index(request, app_dict))

        bucket_template = self._select_bucket_template(app_label)
        context.update({
            'app': app_dict,
            'bucket_template': bucket_template,
        })

        return TemplateResponse(request, self.app_index_template or self._select_index_template(app_label), context, current_app=self.name)

    def bucket_for_app(self, request, app_label, context):
        app_dict = self._get_app_dict(request, app_label, context)
        if not app_dict:
            raise http.Http404('The requested admin page does not exist.')

        # add content from ModelAdmin and/or AppAdmin
        if app_label in self._registered_apps:
            app_dict.update(self._registered_apps[app_label].bucket(request, app_dict))

        context.update({
            'app': app_dict,
        })

        app_bucket = get_template(self._select_bucket_template(app_label))
        return app_bucket.render(RequestContext(request, context))

    def _select_index_template(self, app_label):
        templates = [
            'admin/%s/index.html' % app_label,
            'admin/%s/bucket.html' % app_label,
            'admin/%s_index.html' % app_label,
            'admin/%s_bucket.html' % app_label,
            'admin/appadmin_index.html',
            'admin/appadmin_bucket.html',
        ]

        for template_name in templates:
            try:
                find_template(template_name)
                return template_name
            except TemplateDoesNotExist:
                continue
        return 'admin/appadmin/app_index.html'

    def _select_bucket_template(self, app_label):
        templates = [
            'admin/%s/app_bucket.html' % app_label,
            'admin/%s_bucket.html' % app_label,
            'admin/app_bucket.html',
        ]

        for template_name in templates:
            try:
                find_template(template_name)
                return template_name
            except TemplateDoesNotExist:
                continue
        return 'admin/appadmin/app_bucket.html'

    def _get_app_dict(self, request, app_label, extra_context):
        user = request.user
        has_module_perms = user.has_module_perms(app_label)
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                if has_module_perms:
                    perms = model_admin.get_model_perms(request)

                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        info = (app_label, model._meta.module_name)
                        model_dict = {
                            'name': capfirst(model._meta.verbose_name_plural),
                            'admin_url': reverse('admin:%s_%s_changelist' % info, current_app=self.name),
                            'add_url': reverse('admin:%s_%s_add' % info, current_app=self.name),
                            'perms': perms,
                        }
                        if app_dict:
                            app_dict['models'].append(model_dict),
                        else:
                            # First time around, now that we know there's
                            # something to display, add in the necessary meta
                            # information.
                            app_dict = {
                                'name': app_label.title(),
                                'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                            }

        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda model: model['name'])

        return app_dict


class AppAdmin(object):
    def __init__(self, app_admin_site):
        self.app_admin_site = app_admin_site

    def register(self, model_or_iterable, admin_class=None, **options):
        admin_site = admin.site
        return admin_site.register(model_or_iterable, admin_class, **options)

    def bucket(self, request, app_dict):
        return {}

    def index(self, request, app_dict):
        return self.bucket(request, app_dict)
