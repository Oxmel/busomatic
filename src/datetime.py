#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Name : datetime.py
# Get current time and date, translate date to French

import time
import os

# Setup timezone
os.environ['TZ'] = 'Europe/Paris'
time.tzset()

# Request time (24h format)
def getTime():
    cur_time=time.strftime('%Hh%M')
    return cur_time

# Request date and translate it
def getDate():
    cur_day=time.strftime('%A')
    cur_dayn=time.strftime('%d')
    cur_month=time.strftime('%B')

    dico_jour = {'Monday':'Lun.',
            'Tuesday':'Mar.',
            'Wednesday':'Mer.',
            'Thursday':'Jeu.',
            'Friday':'Ven.',
            'Saturday':'Sam.',
            'Sunday':'Dim.'}
    for word, replace in dico_jour.items():
        cur_day=cur_day.replace(word, replace)

    dico_mois = {'January':'Janv.',
            'February':'Fev.',
            'March':'Mars',
            'April':'Avr.',
            'May':'Mai',
            'June':'Juin',
            'July':'Juil.',
            'August':'Aout',
            'September':'Sept.',
            'October':'Oct.',
            'November':'Nov.',
            'December':'Dec.'}
    for word, replace in dico_mois.items():
        cur_month=cur_month.replace(word, replace)

    return (cur_day+' '+cur_dayn+' '+cur_month)
