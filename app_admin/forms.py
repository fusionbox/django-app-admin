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

    def __init__(self, *args, **kwargs):
        self.fieldset = {
            'classes': '',
            'name': '',
            'description': '',
        }
        if 'fieldset' in kwargs:
            self.fieldset.update(kwargs.pop('fieldset'))
        super(AsAdminForm, self).__init__(*args, **kwargs)

    def start(self):
        return mark_safe('<fieldset class="module aligned {fieldset__classes}">{fieldset__name}{fieldset__description}'.format(
            fieldset__classes=self.fieldset['classes'],
            fieldset__name=self.fieldset['name'] and '<h2>{0}</h2>\n'.format(self.fieldset['name']) or '',
            fieldset__description=self.fieldset['description'] and '<div class="description">{0}</div>\n'.format(self.fieldset['description']) or '',
        ))

    def end(self):
        return mark_safe('''
</fieldset>
'''[1:-1]
        )

    def as_admin(self):
        "Returns this form rendered like it is in the django admin"
        return self.start() + self._html_output(
            normal_row=u'<div%(html_class_attr)s><div>%(label)s %(field)s%(help_text)s</div></div>',
            error_row=u'%s',
            row_ender='</div>',
            help_text_html=u' <p class="help">%s</span>',
            errors_on_separate_row=True
            ) + self.end()

    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return AdminBoundField(self, field, name)


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
