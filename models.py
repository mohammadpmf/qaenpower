from my_datetime import get_jnow


class Staff():
    def __init__(self, name, surname, username, password, access_level, wrong_times, id=None):
        self.name=name
        self.surname=surname
        self.username=username
        self.password=password
        self.access_level=access_level
        self.wrong_times=wrong_times
        self.id=id


class Part():
    def __init__(self, title, id=None):
        self.title=title
        self.id=id


class Place():
    def __init__(self, title, part_id, id=None):
        self.title=title
        self.part_id=part_id
        self.id=id


class Counter():
    def __init__(self, part, place, name, variable_name, previous_value=0, current_value=0, formula='',
                 type='counter', default_value=0, unit=None, warning_lower_bound=None,
                 warning_upper_bound=None, alarm_lower_bound=None, alarm_upper_bound=None, id=None):
        self.part = part
        self.place = place
        self.name = name
        self.variable_name = variable_name
        self.previous_value = previous_value
        self.current_value = current_value
        self.formula = formula
        self.type = type                                    # counter               -   fixed   -  calculating
        self.default_value = default_value                  # previous day number   -   0       -  None
        self.unit = unit
        self.warning_lower_bound = warning_lower_bound      # if not in range => bg yellow
        self.warning_upper_bound = warning_upper_bound      # if not in range => bg yellow
        self.alarm_lower_bound = alarm_lower_bound          # if not in range => bg red
        self.alarm_upper_bound = alarm_upper_bound          # if not in range => bg red
        self.id = id


class CounterLog():
    def __init__(self, value, counter_id, date_time=None, id=None):
        self.value=value
        if date_time!=None:
            self.date_time=date_time
        else:
            self.date_time=get_jnow()
        self.counter_id=counter_id
        self.id=id
