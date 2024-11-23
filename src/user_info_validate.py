
import re
import parsedatetime
from datetime import datetime

def extract_date(user_input):
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(user_input)
    
    if parse_status == 1: 
        parsed_date = datetime(*time_struct[:6])  
        return parsed_date.date()  
    return None


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_phone_number(phone_number):
    return phone_number.isdigit() and len(phone_number) == 10
