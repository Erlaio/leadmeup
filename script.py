# -*- coding: utf-8 -*-
import datetime
import os
import subprocess

import requests
import win32con
import win32gui
from bs4 import BeautifulSoup


def date_check(date: int) -> str:
    """
    Функция проверяет число на соответствие формату даты, и если не соответствует то исправляет его.
    """
    date = str(date)
    if len(date) < 2:
        date = ''.join(('0', date))

    return date


def comma_printer(number: float) -> str:
    """
    Функция добавляет запятую после первого числа(нужна для красивого вывода).
    """
    number = str(round(number))
    new_numbers = ','.join([number[0], number[1:]])
    return new_numbers


def monthly_rate_parse(date_month: int) -> float:
    """
    Функция по заданной дате получает значение monthly rate с сайта банка канады.
    """
    monthly_rate_data = requests.get(
        'https://www.bankofcanada.ca/valet/observations/group/FX_RATES_MONTHLY/?start_date=2021-{}-01'.format(
            date_check(date_month))).json()

    return float(monthly_rate_data['observations'][0]['FXMUSDCAD']['v'])


def yearly_rate_parse(date_year: int) -> float:
    """
    Функция по заданной дате получает значение yearly rate с сайта банка канады.
    """
    yearly_rate_data = requests.get(
        'https://www.bankofcanada.ca/valet/observations/group/FX_RATES_ANNUAL?start_date={}-01-01'.format(
            date_year)).json()

    return float(yearly_rate_data['observations'][0]['FXAUSDCAD']['v'])


def currency_parse(date_month: int, date_year: int) -> float:
    """
    Функция по заданной дате получает значение курса Доллара США с сайта центробанка.
    """
    request = requests.get(
        'https://www.cbr.ru/eng/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To=01.{}.{}'.format(
            date_check(date_month), date_year))
    data = BeautifulSoup(request.content, 'lxml')

    return float(data.find('td', string='US Dollar').find_next('td').text)


current_date = datetime.datetime.now()
current_date_month = int(
    input('\nТекущий месяц-год: {}-{}\nВведите месяц для которого нужно рассчитать зарплату: '.format(
        current_date.month, current_date.year)))
# hour_worked = input('\nВведите значение Actual hour worked: ') - возможна реализация позже

tax_rate = 0.94
yearly_rate = yearly_rate_parse(current_date.year - 1)
monthly_rate = monthly_rate_parse(current_date_month)
currency_value = currency_parse(current_date_month + 1, current_date.year)

compensation = round(30 * yearly_rate / monthly_rate, 2)
salary = round(70000 / currency_value, 2)
net = round(salary + compensation, 2)
total = round(net / tax_rate, 2)
tax = round(total - net, 2)

with open('итог.txt', 'w', encoding='utf-8') as file_result:
    file_result.write(
        f'На {date_check(current_date_month + 1)}.01.{current_date.year}\n1$ = {currency_value} ₽\n'
        f'Individual Entrepreneur Account Fee Compensation — ($30 * {yearly_rate}) / {monthly_rate} = ${compensation}\n'
        # f'Actual hour worked — {hour_worked}\n' - возможна реализация позже
        f'Salary — ₽70,000 / ₽{currency_value} = ${salary}\n'
        f'Net — {net}\n'
        f'Tax — {tax}\n'
        f'Total — {net} / {tax_rate} = {comma_printer(total)}\n')

win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_HIDE)

subprocess.Popen(os.path.abspath('итог.txt'), shell=True)
