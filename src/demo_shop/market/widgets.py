from django.forms.widgets import FileInput, CheckboxInput, Select
from django.utils.translation import gettext_lazy as _

class MyImageInput(FileInput):
    template_name = "market/widgets/image.html"

    class Media:
        css = {
            'all': ('market/css/image.css','market/typcn/typicons.css'),
        }
        js = ('market/js/image.js',)

class MyCheckboxInput(CheckboxInput):
    template_name = "market/widgets/checkbox.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["text"] = self.text
        return context

    def __init__(self, text=_("Should option be active"), attrs=None, check_test=None):
        self.text = text
        super().__init__(attrs,check_test)
    
    class Media:
        css = {
            'all': ('market/css/checkbox.css','market/typcn/typicons.css'),
        }
        js = ('market/js/checkbox.js',)

class MySelectInput(Select):
    template_name = "market/widgets/select.html"
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["text"] = self.text
        return context

    def __init__(self, text=_("Your Choice"), attrs=None, choices=()):
        self.text = text
        super().__init__(attrs,choices)

    class Media:
        css = {
            'all': ('market/css/select.css','market/typcn/typicons.css'),
        }
        js = ('market/js/select.js',)
