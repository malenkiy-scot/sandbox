#!/apollo/env/envImprovement/bin/python3

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone

import re
import json
import time
import logging
import argparse

URL = "https://app.appointmentking.com/scheduler_self_service.php?domid=1342"

RE_PHPSESSID = re.compile(br'name="PHPSESSID".*value="(.*?)"\s\.*')
RE_SESSID = re.compile(br'name="sessid".*value="(.*?)"\s\.*')
RE_LOGIN_PAGERANDVALUE = re.compile(br'name="login_pagerandval".*value="(.*?)"\.*')


def get_and_parse_login_page():
    response = urlopen(URL)
    response_txt = response.read().split(b'\n')
    session_id = None
    pagerandval = None

    for line in response_txt:
        if session_id and pagerandval:
            break
        m = RE_PHPSESSID.search(line)
        if m:
            session_id = m.group(1)
            continue
        m = RE_LOGIN_PAGERANDVALUE.search(line)
        if m:
            pagerandval = m.group(1)
            continue

    return {
        "PHPSESSID": session_id,
        "login_pagerandval": pagerandval,
    }


def get_and_parse_welcome_page(query):
    query.update({
        "login_donesubmit": 'T',
        "location": '1342',
        "first_name": 'Aron',
        "last_name": 'Matskin',
        "dob": '1970-03-07',
        "dob_month": '03',
        "dob_day": '07',
        "dob_year": '1970',
        "email": 'aron.matskin@gmail.com',
        "phone": '617-583-0014',
        "submitbtn_login": 'Find Me!'
    })

    data = bytes(urlencode(query, encoding='utf8'), encoding='utf8')

    request = Request(URL, data, method='POST')
    response = urlopen(request)

    response_txt = response.read().split(b'\n')

    sessid = None
    valid = False

    for line in response_txt:
        if valid and sessid:
            break
        valid |= (line.find(b'Welcome, Aron!') != -1)
        m = RE_SESSID.search(line)
        if m:
            sessid = m.group(1)
    else:
        raise UserWarning("Did not obtain welcome page")

    return {"sessid": sessid}


def get_appointment_data(query, appointment_type_id):
    query.update({
        "request": "get_list",
        "date_filter": "-1",
        "appointment_type_filter": "29726",
        "trainer_filter": "-1",
        "appt_sel": "",
        "external_cal": "false"
    })

    data = bytes(urlencode(query, encoding='utf8'), encoding='utf8')
    # print(data)
    request = Request(URL, data=data, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
    response = urlopen(request)
    _appointment_list = json.loads(response.read())

    items = []
    for item in _appointment_list:
        if item.get('appointment_type_id') == appointment_type_id:
            items.append(item)

    return items


def make_appointment(sessid, appointment_list):
    for appointment in appointment_list:
        logging.info("Checking appointment: %r", appointment)

        date_yyyy_mm_dd = appointment.get('date')
        appointment_datetime = datetime.strptime(date_yyyy_mm_dd, "%Y-%m-%d")
        est_tz = timezone(timedelta(hours=-5), "EST")
        now = datetime.now(est_tz)

        # do not make an appointment for the same date
        if now.day == appointment_datetime.day:
            logging.warning("Not making an appointment for the same day")
            continue

        _year = appointment_datetime.year
        _month = appointment_datetime.month
        _day = appointment_datetime.day

        if _year == 2021 and _month == 5:
            if _day == 17 or _day == 18:
                logging.warning("Not making an appointment on Shavuos")
                continue

        if appointment_datetime.isoweekday() == 6:
            logging.warning("Not making an appointment on Saturday")
            continue

        for time_slot in appointment.get('times', []):
            time_24 = time_slot.get('time_24')
            if not time_24:
                loggint.warning("Invalid time slot")
                continue
            try:
                hour = int(time_24.split(':')[0])
                if hour < 7:
                    logging.warning("Skipping an early time slot at %d", hour)
                    continue

                appointment_id = appointment.get('appointment_id')
                appointment_type_id = appointment.get('appointment_type_id')
            except Exception:
                logging.warning("Error getting information from time slot %r", time_slot)
                continue

            datetime_str = date_yyyy_mm_dd + ' ' + time_24 + ':00'
            availability_id = appointment.get('availability_id', '')
            if not availability_id:
                availability_id = ''

            logging.info('Making an appointment for %s', datetime_str)

            query = {
                'request': 'make_request',
                'sessid': sessid,
                'datetime': datetime_str,
                'appointment_type_id': appointment_type_id,
                'appointment_id': appointment_id,
                'availability_id': availability_id
            }

            data = bytes(urlencode(query, encoding='utf8'), encoding='utf8')
            # print(data)
            response = urlopen(URL, data=data)

            response_body = json.loads(response.read())
            success = response_body.get("success", 0)
            if not success:
                error = response_body.get("error", "")
                logging.error('Failed to make the appointment: %s', error)
            else:
                logging.warning('Successfully made the appointment for %s', datetime_str)
                return True
    else:
        return False


def main():
    query1 = get_and_parse_login_page()
    query2 = get_and_parse_welcome_page(query1)
    sessid = query2.get("sessid", "")

    # appointment_types = {"28345": "Family swim"}
    appointment_types = {
        "33172": "ILS-10",
        "33173": "ILS-8",
        "33174": "ILS-6",
        "33175": "ILS-4",
        "33176": "ILS-2",
        "33178": "LSE-12",
        "33179": "LSE-8",
        "33180": "LSE-6",
        "33181": "LSE-4",
        }

    start = time.time()
    now = start

    while now - start < 60*5 and appointment_types:  # run for 5 minutes
        for appointment_type_id in appointment_types:
            logging.debug("Looking for %s appointments", appointment_types[appointment_type_id])
            appointment_list = get_appointment_data(query2, appointment_type_id)

            if not appointment_list:
                logging.info("Did not find any appointments for %s", appointment_types[appointment_type_id])
                continue
            logging.info("Found appointments for %s", appointment_types[appointment_type_id])

            # print(appointment_data)
            if make_appointment(sessid, appointment_list):
                del(appointment_types[appointment_type_id])
                break
        
        seconds_after_hour = now % 3600
        sleep_time = 1 if seconds_after_hour > 3570 or seconds_after_hour < 30 else 5
        time.sleep(sleep_time)
        now = time.time()


def parser():
    parser = argparse.ArgumentParser(description="Make YMCS appointments automatically")
    
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--debug', '-vv', action="store_const", const=logging.DEBUG, default=0)
    verbosity_group.add_argument('--verbose', '-v', action="store_const", const=logging.INFO, default=0)
    verbosity_group.add_argument('--quiet', '-q', action="store_const", const=logging.ERROR, default=0)

    return parser

if __name__ == '__main__':
    args = parser().parse_args()

    est_tz = timezone(timedelta(hours=-5), "EST")
    now = datetime.now(est_tz)

    LOGGING_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    log_level = args.debug or args.verbose or args.quiet or logging.WARNING

    logging.basicConfig(format=LOGGING_FORMAT, level=log_level, datefmt=DATE_FORMAT)

    logging.info("Starting a run at %s", now.strftime(DATE_FORMAT))
    main()
    logging.info("Ended a run at %s", now.strftime(DATE_FORMAT))
