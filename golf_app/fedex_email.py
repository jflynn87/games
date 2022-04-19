from email.message import EmailMessage
import imp
from multiprocessing.spawn import import_main_path
import django
from django.core.mail import send_mail
from django.template.loader import get_template
from requests import request
from golf_app.views import fedEx_summary_context_data as fedex_data
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template, Context
from django.shortcuts import render
from django.http import HttpRequest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime

import time



def send_summary_email():
    start = datetime.now()
    context = fedex_data()
    
    dir = settings.BASE_DIR + '/golf_app/templates/golf_app/'
    #msg_plain = render_to_string(dir + 'email.txt', {'appt': appt})
    #msg_html = render_to_string(dir + 'fedex_summary.html', context)
    #msg = EmailMessage(msg_html)
    print ('post msg_html')
    t = Template(dir + 'fedex_summary.html')
    c = Context(context)
    #html =  t.render(c)
    req = HttpRequest()
    print (render(req, dir + 'fedex_summary.html', context, content_type='application/xhtml+xml').__dict__)    
    
    
    #print(msg)
    #send_mail("Test FedEx ",
    #from_email = "jflynn87g.gmail.com",
    #recipient_list = ['jflynn87@hotmail.com',],
    #message = msg
    ##html_message=msg,
    # )

    return

