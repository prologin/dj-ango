from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import PrependedText, StrictButton
from django.contrib.auth.forms import AuthenticationForm


class DjAuthenticationForm(AuthenticationForm):
    helper = FormHelper()
    helper.form_tag = True
    helper.form_show_labels = False
    helper.layout = Layout(
        PrependedText('username',
                      '<i class="fa fa-user"></i>'),
        PrependedText('password',
                      '<i class="fa fa-lock"></i>'),
        StrictButton('Connect',
                     css_class='btn-default btn-block',
                     type='submit'), )
