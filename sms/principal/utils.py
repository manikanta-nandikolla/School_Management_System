from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from django.conf import settings
import os


def render_to_pdf(template_src, context_dict):
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=os.path.join(settings.BASE_DIR, 'static'))
    pdf = html.write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')