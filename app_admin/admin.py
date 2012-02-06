from django import http
from django.template.response import TemplateResponse
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache


from django.contrib import admin
from django.contrib.admin.sites import AdminSite


class AppAdminSite(AdminSite):
    _registered_apps = {}

    def register_app(self, app_admin_class):
        if app_admin_class not in self._registered_apps:
            self._registered_apps[app_admin_class] = app_admin_class()
        return self._registered_apps[app_admin_class]

    @never_cache
    def index(self, request, extra_context=None):
        return super(AppAdminSite, self).index(request, extra_context)

        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

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
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, [
            self.index_template or 'admin/index.html',
        ], context, current_app=self.name)

    @never_cache
    def app_index(self, request, app_label, extra_context=None):
        return super(AppAdminSite, self).app_index(request, app_label, extra_context)

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
                                'app_url': '',
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                            }
        if not app_dict:
            raise http.Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(key=lambda x: x['name'])
        context = {
            'title': _('%s administration') % capfirst(app_label),
            'app_list': [app_dict],
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context, current_app=self.name)


class AppAdmin(object):
    def register(self, model_or_iterable, admin_class=None, **options):
        admin_site = admin.site
        return admin_site.register(model_or_iterable, admin_class, **options)
