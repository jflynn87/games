from email.message import EmailMessage
import imp
from multiprocessing.spawn import import_main_path
import django
from django.core.mail import send_mail
from django.template.loader import get_template
from requests import request
#from golf_app.views import fedEx_summary_context_data as fedex_data

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



def send_summary_email(dist):
    '''takes a list of email addresses, returns nothing'''
    from golf_app.views import FedExSummaryEmail
    start = datetime.now()
    req = HttpRequest()
    context = FedExSummaryEmail().get_context_data()
    
    dir = settings.BASE_DIR + '/golf_app/templates/golf_app/'
    #msg_plain = render_to_string(dir + 'email.txt', {'appt': appt})
    msg = render_to_string(dir + 'fedex_summary_email.html', context)
    #msg = EmailMessage(msg_html)
    print ('post msg_html')
    t = Template(dir + 'fedex_summary_email.html')
    c = Context(context)
    #html =  t.render(c)
    req = HttpRequest()
    #print (render(req, dir + 'fedex_summary.html', context, content_type='application/xhtml+xml').__dict__)    
    
    
    #print(msg)
    send_mail("Weekly Golf Game Update ",
    from_email = "jflynn87g.gmail.com",
    #recipient_list = ['jflynn87@hotmail.com','jrc7825@gmail.com', 'ryosuke.aoki0406@gmail.com'],
    #recipient_list = ['jflynn87@hotmail.com',],
    recipient_list = dist,
    message = msg,
    html_message=msg,
     )

    return

