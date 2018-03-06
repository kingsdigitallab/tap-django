from django.db import models
from django.forms import fields, widgets
from django.forms.utils import ValidationError


class JavaScriptWidget(widgets.Textarea):
    template_name = 'chirp/javascript_widget.html'

    class Media:
        css = {
            'all': ['vendor/codemirror/lib/codemirror.css',
                    'vendor/codemirror/theme/solarized.css']
        }
        js = ['vendor/codemirror/lib/codemirror.js',
              'vendor/codemirror/mode/javascript/javascript.js',
              'vendor/codemirror/addon/selection/active-line.js',
              'vendor/codemirror/addon/edit/matchbrackets.js',
              'js/admin.js']


class JavaScriptFormField(fields.CharField):
    widget = JavaScriptWidget

    def clean(self, value):
        if not value and not self.required:
            return None

        try:
            return super(JavaScriptFormField, self).clean(value)
        except TypeError:
            raise ValidationError('Enter valid JavaScript')


class JavaScriptField(models.TextField):
    form_class = JavaScriptFormField

    def formfield(self, **kwargs):
        field = super(JavaScriptField, self).formfield(**kwargs)
        if not field.help_text:
            field.help_text = 'Enter valid JavaScript'

        return field
