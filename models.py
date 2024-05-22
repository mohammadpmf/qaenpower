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


class Parameter():
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


class ParameterLog():
    def __init__(self, value, workout, is_ok, date, date_time_modified, parameter_id, user_id, id, users_name, users_surname, type=None):
        self.value=value
        self.workout=workout
        self.is_ok=is_ok
        self.date=date
        self.date_time_modified=date_time_modified
        self.parameter_id=parameter_id
        self.user_id=user_id
        self.id=id
        self.users_full_name = f"{users_name} {users_surname}"
        self.type=type

    def __str__(self):
        return f"{self.value}"
