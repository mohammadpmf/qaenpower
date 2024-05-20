from functions import get_jnow


class Staff():
    def __init__(self, name, surname, username, password, access_level, wrong_times, default_date, id):
        self.name=name
        self.surname=surname
        self.username=username
        self.password=password
        self.access_level=access_level
        self.wrong_times=wrong_times
        self.default_date=default_date
        self.id=id

    def __str__(self):
        return f"{self.name} {self.surname}"


class Part():
    def __init__(self, title, id):
        self.title=title
        self.id=id

    def __str__(self):
        return f"{self.title}"


class Place():
    def __init__(self, title, part_id, id, part_title):
        self.title=title
        self.part_id=part_id
        self.id=id
        self.part_title=part_title
    
    def __str__(self):
        return f"{self.title}"


class Counter():
    def __init__(self, part, place, name, variable_name, formula, type, default_value, unit,
                 warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound,
                 id, place_title=None, part_title=None):
        self.part = part
        self.place = place
        self.name = name
        self.variable_name = variable_name
        self.formula = formula
        self.type = type                                    # counter               -   fixed   -  calculating
        self.default_value = default_value                  # previous day number   -   0       -  None
        self.unit = unit
        self.warning_lower_bound = warning_lower_bound      # if not in range => bg yellow
        self.warning_upper_bound = warning_upper_bound      # if not in range => bg yellow
        self.alarm_lower_bound = alarm_lower_bound          # if not in range => bg red
        self.alarm_upper_bound = alarm_upper_bound          # if not in range => bg red
        self.id = id
        self.place_title = place_title
        self.part_title = part_title

    def __str__(self):
        return f"{self.name}"


class CounterLog():
    def __init__(self, value, workout, is_broken, date, date_time_modified, counter_id, user_id, id):
        self.value=value
        self.workout=workout
        self.is_broken=is_broken
        self.date=date
        self.date_time_modified=date_time_modified
        self.counter_id=counter_id
        self.user_id=user_id
        self.id=id

    def __str__(self):
        return f"{self.value}"
