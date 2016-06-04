import os
import _csv
import re
import datetime
import calendar

NUM_OF_ARGS = 6


class Fio:
    first_name = ""
    last_name = ""
    patronymic = ""

    def __init__(self):
        self.first_name = ""
        self.last_name = ""
        self.patronymic = ""


class Person:
    fio = Fio()
    phone_number = 0
    date_of_birth = None
    id = 0

    def __init__(self):
        self.fio.__init__()
        self.phone_number = 0
        self.date_of_birth = None
        self.id = 0

    def to_list(self):
        str_ = self.date_of_birth
        list_ = [self.id, self.fio.last_name, self.fio.first_name,
                 self.fio.patronymic, str_.strftime("%d.%m.%Y"), self.phone_number]
        return list_

    def to_str(self):
        str_ = ""
        list_ = self.to_list()
        i = 0
        while i < NUM_OF_ARGS:
            str_ += str(list_[i])
            str_ += " "
            i += 1
        return str_


biggest_id = 0
removal_list = []
clean_id = 0
is_relevant = 1
try:
    file = open('database.csv.txt', 'r+')
except FileNotFoundError:
    file = open('database.csv.txt', 'w+')

writer = _csv.writer(file)
reader = _csv.reader(file)

id_to_person = {}
phone_number_to_id = {}
date_of_birth_to_id = {}
last_name_to_id = {}
first_name_to_id = {}
patronymic_to_id = {}


def check_for_birthday(p):
    date = p.date_of_birth
    now = datetime.datetime.now()
    date = datetime.datetime(year=now.year, month=date.month, day=date.day)
    now = datetime.datetime(year=now.year, month=now.month, day=now.day)
    b = calendar.isleap(now.year + 1)
    if now > date:
        date = datetime.datetime(year=date.year + 1, month=date.month, day=date.day)
    ost = (date - now).days
    if ost < 14:
        print("REMINDER: " + p.fio.last_name + " " + p.fio.first_name +
              " " + p.fio.patronymic + " has a birthday in " + str(ost) + " days")


def add_value_to_list(list_, key, value):
    if list_.get(key) is None:
        list_[key] = [value]
    else:
        list_[key] += [value]


def add_person_to_dictionaries(p):
    id_to_person[p.id] = p
    add_value_to_list(phone_number_to_id, p.phone_number, p.id)
    add_value_to_list(date_of_birth_to_id, p.date_of_birth, p.id)
    add_value_to_list(last_name_to_id, p.fio.last_name, p.id)
    add_value_to_list(first_name_to_id, p.fio.first_name, p.id)
    add_value_to_list(patronymic_to_id, p.fio.patronymic, p.id)


def add_one_line_from_file(line):
    line = line.rstrip()
    mas = line.split(',')
    p = Person()
    p.id = int(mas[0])
    global biggest_id
    if p.id >= biggest_id:
        biggest_id = p.id + 1
    fio = Fio()
    fio.last_name = mas[1]
    fio.first_name = mas[2]
    fio.patronymic = mas[3]
    p.fio = fio
    p.date_of_birth = datetime.datetime.strptime(mas[4], "%d.%m.%Y")
    p.phone_number = mas[5]
    add_person_to_dictionaries(p)
    check_for_birthday(p)


def write_header():
    writer.writerow(["Id", "Last Name", "First Name", "Patronymic", "Date of birth", "Phone number"])


def before_start():
    if os.stat(file.name).st_size != 0:
        lines = file.readlines()
        i = 1
        while i < len(lines):
            add_one_line_from_file(lines[i])
            i += 1
    else:
        write_header()


def refresh():
    global is_relevant
    global clean_id
    global biggest_id
    global removal_list

    if is_relevant == 0:
        file.seek(0)
        file.truncate()
        write_header()
        i = clean_id
        new_biggest_id = 0
        while i < biggest_id:
            if i not in removal_list:
                try:
                    p = id_to_person[i]
                    writer.writerow(p.to_list())
                    if new_biggest_id <= i:
                        new_biggest_id = i + 1
                except KeyError:
                    pass
            i += 1
        file.flush()
        biggest_id = new_biggest_id
        clean_id = 0
        is_relevant = 1
        removal_list = []


def clean():
    global clean_id
    global removal_list
    global id_to_person
    global phone_number_to_id
    global date_of_birth_to_id
    global last_name_to_id
    global first_name_to_id
    global patronymic_to_id
    global is_relevant

    clean_id = biggest_id
    is_relevant = 0

    removal_list = []
    id_to_person.clear()
    date_of_birth_to_id.clear()
    phone_number_to_id.clear()
    last_name_to_id.clear()
    first_name_to_id.clear()
    patronymic_to_id.clear()


def delete_id_from_list(list_, key, id_to_delete):
    list_new = list_[key]
    list_.pop(key)
    list_new.remove(id_to_delete)
    list_[key] = list_new


def delete(id_to_delete):
    p = id_to_person[id_to_delete]
    print("Do you want to delete this one? (Y/N)")
    print(str(p.to_str()))
    inp = input()
    if inp == 'y':
        id_to_person.pop(id_to_delete)

        delete_id_from_list(first_name_to_id, p.fio.first_name, id_to_delete)
        delete_id_from_list(last_name_to_id, p.fio.last_name, id_to_delete)
        delete_id_from_list(patronymic_to_id, p.fio.patronymic, id_to_delete)
        delete_id_from_list(date_of_birth_to_id, p.date_of_birth, id_to_delete)
        delete_id_from_list(phone_number_to_id, p.phone_number, id_to_delete)

        global removal_list
        removal_list += [id_to_delete]
        print("Person was deleted")
        global is_relevant
        is_relevant = 0
    else:
        print("Deletion was canceled")


def action(list_id, field, act_):
    n = len(list_id)
    if n > 0:
        n = len(list_id)
        more_than_1 = n > 1
        verb = "are " if more_than_1 else "is "
        ending = "s" if more_than_1 else ""
        print("There " + verb + str(n) + " person " + ending + "with this " + field)
        i = 0
        while i < n:
            print(str(i) + ":", end='  ')
            print(id_to_person[list_id[i]].to_str())
            i += 1

        if act_ == "d":
            if more_than_1:
                print("Delete n'th     --> print number(counting from 0)")
                print("Cancel deletion --> c")
                inp = input()
                if inp == "c":
                    return
                else:
                    delete(list_id[int(inp)])
            else:
                delete(list_id[0])
    if n == 0:
        print("There is no person with this " + field)


def check(all_list, val):
    try:
        list_id = all_list[val]
        return list_id
    except KeyError:
        print("There is no such person")
        return None


def action_launcher(value, all_list, name_of_list, type_of_action):
    list_id = check(all_list, value)
    if list_id is not None:
        action(list_id, name_of_list, type_of_action)


def act_by_id(id_, type_of_action):
    try:
        str_ = id_to_person[id_].to_str()
        if type_of_action == "d":
            delete(id_)
        else:
            print("There is your person:")
            print(str_)
    except KeyError:
        print("There is no such person")


def standardize(inp: str):
    inp = inp.lower()
    ch = inp[0].upper()
    inp = ch + inp[1:]
    return inp


def date_input():
    i = 0
    date = None
    while i < 2:
        try:
            date = datetime.datetime.strptime(input(), "%d.%m.%Y")
            break
        except ValueError:
            print("WRONG INPUT")
            if i == 0:
                print("Try again:")
            else:
                print("FAILED")
        i += 1

    return date


def reg_input(str_: str) -> str:
    i = 0
    phone_number = None
    pattern = re.compile(str_)
    while i < 2:
        inp = input()
        pattern = pattern.match(inp)
        if pattern is None:
            if i == 0:
                print("WRONG INPUT")
                print("Try again:")
            else:
                print("FAILED")
        else:
            phone_number = inp
            break
        i += 1
    return str(phone_number)


def printing_choice(type_of_action):
    print("last name       --> print ln")
    print("first name      --> print fn")
    print("patronymic      --> print p")
    print("date of birth   --> print db")
    print("phone number    --> print pn")
    print("ID              --> print id")
    print("go back         --> print b")
    inp = input()
    inp = inp.lower()
    if inp == "ln":
        print("Enter last name: ")
        last_name = reg_input("[A-Za-zА-Яа-я]+")
        if last_name is None:
            return
        action_launcher(standardize(last_name), last_name_to_id, "last name", type_of_action)
    elif inp == "fn":
        print("Enter first name:")
        first_name = reg_input("[A-Za-zА-Яа-я]+")
        if first_name is None:
            return
        action_launcher(standardize(first_name), first_name_to_id, "first name", type_of_action)
    elif inp == "p":
        print("Enter patronymic:")
        patronymic = reg_input("[A-Za-zА-Яа-я]+")
        if patronymic is None:
            return
        action_launcher(standardize(patronymic), patronymic_to_id, "patronymic", type_of_action)
    elif inp == "db":
        print("Enter date of birth (dd.mm.yyyy):")
        date_of_birth = date_input()
        if date_of_birth is None:
            return
        action_launcher(date_of_birth, date_of_birth_to_id, "date_of_birth", type_of_action)
    elif inp == "pn":
        print("Enter phone number")
        phone_number = reg_input("[+]?[0-9]+")
        if inp is None:
            return
        action_launcher(phone_number, phone_number_to_id, "phone_number", type_of_action)
    elif inp == "id":
        print("Enter ID")
        id_ = reg_input("[0-9]+")
        act_by_id(int(id_), type_of_action)
    elif inp != "b":
        print("WRONG INPUT")


def input_person():
    global biggest_id
    per = Person()
    fio = Fio()
    print("last name:")
    last_name = reg_input("[A-Za-zА-Яа-я]+")
    if last_name is None:
        return
    fio.last_name = standardize(last_name)

    print("first name:")
    first_name = reg_input("[A-Za-zА-Яа-я]+")
    if fio is None:
        return
    fio.first_name = standardize(first_name)

    print("patronymic:")
    patronymic = reg_input("[A-Za-zА-Яа-я]+")
    if patronymic is None:
        return
    fio.patronymic = standardize(patronymic)

    per.fio = fio

    print("date of birth (dd.mm.yyyy):")
    date = date_input()
    if date is None:
        return
    per.date_of_birth = date

    print("phone number:")
    phone_number = reg_input("[+]?[0-9]+")
    if phone_number is None:
        return
    per.phone_number = phone_number

    per.id = biggest_id
    biggest_id += 1

    add_person_to_dictionaries(per)
    global is_relevant
    is_relevant = 0


def start():
    while 1:
        print("------------------------------------------------------------------------")
        print("Add a person      --> print A(a)")
        print("Delete a person   --> print D(d)")
        print("Find a person     --> print F(f)")
        print("Clean database    --> print C(c)")
        print("Refresh table     --> print R(r)")
        print("Check if relevant --> print CH(ch)")
        print("Exit              --> print E(e)")

        inp = input()
        inp = inp.lower()

        if inp == "a":
            print("ADD A PERSON:")
            input_person()
        elif inp == "d":
            print("DELETE A PERSON by ")
            printing_choice("d")
        elif inp == "f":
            print("FIND A PERSON by ")
            printing_choice("f")
        elif inp == "c":
            clean()
            print("Base was cleaned")
        elif inp == "e":
            refresh()
            file.close()
            return
        elif inp == "r":
            refresh()
        elif inp == "ch":
            print("Base " + ("is" if is_relevant else "MAY NOT be") + " relevant")
        else:
            print("No such command")


before_start()
start()
