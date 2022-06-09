from sys import platform
from babel.dates import format_date
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk
from tkcalendar import Calendar,DateEntry
import re

class CustomCalendar(Calendar):
    def _get_date_pattern(self,date_pattern,locale=None):
        """
        Return the babel pattern corresponding to date_pattern.

        If date_pattern is 'short', return the pattern correpsonding to the
        locale, else return date_pattern if valid.

        A valid pattern is a sequence of y, m and d
        separated by non letter characters, e.g. yyyy-mm-dd or d/m/yy
        """
        if locale is None:
            locale = self._properties['locale']
        if date_pattern == 'short':
            return get_date_format('short',locale).pattern
        pattern = date_pattern.lower()
        ymmd = r'^y+[^a-zA-Z]*m{1,3}&m{1,3}[^a-z]*d{1,2}[^mdy]*$'
        ymd = r'^y+[^a-zA-Z]*m{1,3}[^a-z]*d{1,2}[^mdy]*$'
        mdy = r'^m{1,2}[^a-zA-Z]*d{1,2}[^a-z]*y+[^mdy]*$'
        dmy = r'^d{1,2}[^a-zA-Z]*m{1,2}[^a-z]*y+[^mdy]*$'
        res = ((re.search(ymmd,pattern) is not None)
               or (re.search(ymd,pattern) is not None)
               or (re.search(mdy,pattern) is not None)
               or (re.search(dmy,pattern) is not None))
        if res:
            return pattern.replace('m','M')
        raise ValueError('{} is not a valid date pattern'.format(date_pattern))

    def format_date(self,date=None):
        """Convert date (datetime.date) to a string in the locale."""
        return format_date(date,self._properties['date_pattern'],self._properties['locale']).replace('&','')

    def parse_date(self,date):
        """Parse string date in the locale format and return the corresponding datetime.date."""
        try:
            date_format = self._properties['date_pattern'].lower()
            ny = date_format.count('y')
            nm = date_format.count('m')
            nd = date_format.count('d')
            if nm == 5:
                ymd = r'^y+([^a-zA-Z]*)mm&mmm([^a-z]*)d{1,2}([^mdy]*)$'
                m = re.search(ymd,date_format)
                if not m:
                    raise ValueError('{} is not a valid date format'.format(date_format))
                sep1 = m.group(1)
                sep2 = m.group(2)
                sep3 = m.group(3)
                ymd = '^('+'\d'*ny+')'+sep1+'\d\d&('+'[a-zA-Z]'*3+')'+sep2+'('+'\d'*nd+')'+sep3+'$'
                m = re.search(ymd,date)
                if not m:
                    raise ValueError('{} is not a valid date'.format(date))
                year = m.group(1)
                if len(year) == 2:
                    year = 2000 + int(year)
                else:
                    year = int(year)
                month = self.strptime(m.group(2),'%b').month
                day = int(m.group(3))
            elif nm == 3:
                ymd = r'^y+([^a-zA-Z]*)mmm([^a-z]*)d{1,2}([^mdy]*)$'
                m = re.search(ymd,date_format)
                if not m:
                    raise ValueError('{} is not a valid date format'.format(date_format))
                sep1 = m.group(1)
                sep2 = m.group(2)
                sep3 = m.group(3)
                ymd = '^('+'\d'*ny+')'+sep1+'('+'[a-zA-Z]'*nm+')'+sep2+'('+'\d'*nd+')'+sep3+'$'
                m = re.search(ymd,date)
                if not m:
                    raise ValueError('{} is not a valid date'.format(date))
                year = m.group(1)
                if len(year) == 2:
                    year = 2000 + int(year)
                else:
                    year = int(year)
                month = self.strptime(m.group(2),'%b').month
                day = int(m.group(3))
            else:
                year_idx = date_format.index('y')
                month_idx = date_format.index('m')
                day_idx = date_format.index('d')
                indexes = [(year_idx,'Y'),(month_idx,'M'),(day_idx,'D')]
                indexes.sort()
                indexes = dict([(item[1],idx) for idx,item in enumerate(indexes)])
                numbers = re.findall(r'(\d+)',date)
                year = numbers[indexes['Y']]
                if len(year) == 2:
                    year = 2000 + int(year)
                else:
                    year = int(year)
                month = int(numbers[indexes['M']])
                day = int(numbers[indexes['D']])
                if month > 12:
                    month,day = day,month
            return self.date(year,month,day)
        except Exception:
            return self.datetime.today()

class CustomDateEntry(DateEntry):
    def __init__(self,master=None,**kw):
        """
        Create an entry with a drop-down calendar to select a date.

        When the entry looses focus, if the user input is not a valid date,
        the entry content is reset to the last valid date.

        Keyword Options
        ---------------

        usual ttk.Entry options and Calendar options.
        The Calendar option 'cursor' has been renamed
        'calendar_cursor' to avoid name clashes with the
        corresponding ttk.Entry option.

        Virtual event
        -------------

        A ``<<DateEntrySelected>>`` event is generated each time
        the user selects a date.

        """
        # sort keywords between entry options and calendar options
        kw['selectmode'] = 'day'
        entry_kw = {}

        style = kw.pop('style','DateEntry')

        for key in self.entry_kw:
            entry_kw[key] = kw.pop(key,self.entry_kw[key])
        entry_kw['font'] = kw.get('font',None)
        self._cursor = entry_kw['cursor']  # entry cursor
        kw['cursor'] = kw.pop('calendar_cursor',None)

        ttk.Entry.__init__(self,master,**entry_kw)

        self._determine_downarrow_name_after_id = ''

        # drop-down calendar
        self._top_cal = tk.Toplevel(self)
        self._top_cal.withdraw()
        if platform == 'linux':
            self._top_cal.attributes('-type','DROPDOWN_MENU')
        self._top_cal.overrideredirect(True)
        self._calendar = CustomCalendar(self._top_cal,**kw)
        self._calendar.pack()

        # locale date parsing / formatting
        self.format_date = self._calendar.format_date
        self.parse_date = self._calendar.parse_date

        # style
        self._theme_name = ''   # to detect theme changes
        self.style = ttk.Style(self)
        self._setup_style()
        self.configure(style=style)

        # add validation to Entry so that only dates in the locale's format
        # are accepted
        validatecmd = self.register(self._validate_date)
        self.configure(validate='focusout',
                       validatecommand=validatecmd)

        # initially selected date
        self._date = self._calendar.selection_get()
        if self._date is None:
            today = self._calendar.date.today()
            year = kw.get('year',today.year)
            month = kw.get('month',today.month)
            day = kw.get('day',today.day)
            try:
                self._date = self._calendar.date(year,month,day)
            except ValueError:
                self._date = today
        self._set_text(self.format_date(self._date))

        # --- bindings
        # reconfigure style if theme changed
        self.bind('<<ThemeChanged>>',
                  lambda e: self.after(10,self._on_theme_change))
        # determine new downarrow button bbox
        self.bind('<Configure>',self._determine_downarrow_name)
        self.bind('<Map>',self._determine_downarrow_name)
        # handle appearence to make the entry behave like a Combobox but with
        # a drop-down calendar instead of a drop-down list
        self.bind('<Leave>',lambda e: self.state(['!active']))
        self.bind('<Motion>',self._on_motion)
        self.bind('<ButtonPress-1>',self._on_b1_press)
        # update entry content when date is selected in the Calendar
        self._calendar.bind('<<CalendarSelected>>',self._select)
        # hide calendar if it looses focus
        self._calendar.bind('<FocusOut>',self._on_focus_out_cal)

    def _validate_date(self):
        """Date entry validation: only dates in locale '%x' format are accepted."""
        try:
            date = self.parse_date(self.get())
            self._date = self._calendar.check_date_range(date)
            if self._date != date:
                self._set_text(self.format_date(self._date))
                return False
            else:
                return True
        except (ValueError,IndexError):
            #self._set_text(self.format_date(self._date))
            return False
