# currency_difference

The application shows the difference in exchange rates for two dates.

## Run

To start the server, you need to run **main.py**

    python main.py

## User's manual

The application uses a **currencies.db** database. If it was not created, then the first time the application is launched, it will do it automatically. By default, the database stores the values of the different currencies from 2000-01-01.

View a list of all available currencies:

    http://127.0.0.1:5000/

Viewing the difference in the exchange rate for two dates:

    http://127.0.0.1:5000/?date_req1=DATE1&date_req2=DATE2&iso_char_code=CODE

where:
- **DATE1/DATE2** - two date in format **YYYY-MM-DD**
- **CODE** - currency code in format **AAA**

Example:

    http://127.0.0.1:5000/?date_req1=2002-02-02&date_req2=2002-09-02&iso_char_code=USD
    
If you enter an invalid date format, an error message will appear.

## The work done

The technology stack is listed in the file **requirements.txt**

- **Flask** is used to make http api work
- **Flask_SQLAlchemy** is used to work with the database
- **requests** is used to collect information from the site http://www.cbr.ru/development/sxml/
- **xmltodict** is used to work with xml files
