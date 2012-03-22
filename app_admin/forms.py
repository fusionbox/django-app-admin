"""
Defines classes and fields that are used in the django admin.

AsAdminForm - extend this class, and you will gain a {{ form.as_admin }}
    method on your forms.  Make sure to include {{ form.media }} if
    you want the django admin form css to kick in.

submit.html comes in handy here, too.  It outputs a save button.

Example:

{% block extrastyle %}
  {{ block.super }}
  {{ my_form.media }}
{% endblock %}

{% block content %}
{{ my_form.as_admin }}
{% include "admin/app_admin/submit.html" %}
{% endblock %}

"""
from django import forms
from django.forms.forms import BoundField
from django.utils.safestring import mark_safe


class AsAdminForm(forms.BaseForm):
    """
    In admin, wouldn't it be nice to have `form.as_admin` output?  Welcome!

    But it's not so easy... there is no way to add a class to a field container
    (field? yes, errors? yes, required? yes.  container: ah, django...).
    So we cannot just implement as_admin, we must also subclass
    `BoundField.css_classes` (we call parent with extra_classes+='form-row')
    """
    required_css_class = 'required'
    error_css_class = 'errors'

    def __init__(self, *args, **kwargs):
        """
        Accepts a `fieldset` option that should be a dictionary with the
        following keys:

        classes - classes to apply to the fieldset.
        title - if supplied, it will be surrounded in <h2> tags
        description - if supplied, it will be displayed in div.description
            under the title.
        """
        self.fieldset = {
            'classes': '',
            'title': '',
            'description': '',
        }
        if 'fieldset' in kwargs:
            self.fieldset.update(kwargs.pop('fieldset'))
        super(AsAdminForm, self).__init__(*args, **kwargs)
        if hasattr(self, 'readonly_fields'):
            for name in self.readonly_fields:
                self.fields[name].widget.attrs['readonly'] = 'readonly'
                self.fields[name].widget.attrs['disabled'] = 'disabled'

    def start(self):
        return mark_safe('''
{fieldset__errors}
<fieldset class="module aligned {fieldset__classes}">{fieldset__title}{fieldset__description}
'''[1:-1].format(
            fieldset__errors=self.errors and '<p class="errornote">Please correct the error(s) below.</p>\n' or '',
            fieldset__classes=self.fieldset['classes'],
            fieldset__title=self.fieldset['title'] and '<h2>{0}</h2>\n'.format(self.fieldset['title']) or '',
            fieldset__description=self.fieldset['description'] and '<div class="description">{0}</div>\n'.format(self.fieldset['description']) or '',
        ))

    def end(self):
        return mark_safe('''
</fieldset>
'''[1:-1]
        )

    def as_admin(self, surround=True):
        "Returns this form rendered like it is in the django admin"
        if surround:
            ret = self.start()
        else:
            ret = ''
        ret += self._html_output(
            normal_row=u'<div%(html_class_attr)s>%(errors)s<div>%(label)s %(field)s%(help_text)s</div></div>',
            error_row=u'%s',
            row_ender='</div>',
            help_text_html=u' <p class="help">%s</span>',
            errors_on_separate_row=False
            )
        if surround:
            ret += self.end()
        return mark_safe(ret)

    def as_admin_bare(self):
        return self.as_admin(surround=False)

    def __getitem__(self, name):
        "Returns an AdminBoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return AdminBoundField(self, field, name)

    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }


class AdminBoundField(BoundField):
    def css_classes(self, extra_classes=None):
        """
        Adds 'form-row' to extra_classes.  Since extra_classes is handled
        as a string or list in django.forms, we mimic that behavior.
        """
        if not extra_classes:
            extra_classes = []
        elif hasattr(extra_classes, 'split'):
            extra_classes = extra_classes.split()  # from django.forms.BoundField.css_classes
        extra_classes.append('form-row')
        return super(AdminBoundField, self).css_classes(extra_classes)
