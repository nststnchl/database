import os
import _csv
import re
import datetime
import bisect
import sys


class Fio:
    first_name = ""
    last_name = ""
    patronymic = ""

    def __init__(self, ln, fn, p):
        self.first_name = fn
        self.last_name = ln
        self.patronymic = p


class Person:
    fio = Fio("", "", "")
    phone_number = 0
    date_of_birth = None
    id = 0

    def __init__(self, id_, fio, db, pn):
        self.fio = fio
        self.phone_number = pn
        self.date_of_birth = db
        self.id = id_

    def to_list(self):
        str_ = self.date_of_birth
        list_ = [self.id, self.fio.last_name, self.fio.first_name,
                 self.fio.patronymic, str_.strftime("%d.%m.%Y"), self.phone_number]
        return list_

    def to_str(self):
        str_ = ""
        list_ = self.to_list()
        i = 0
        while i < len(list_):
            str_ += str(list_[i])
            str_ += " "
            i += 1
        return str_


biggest_id = 0
freed_id = []
is_up_to_date = 1
try:
    file = open('database.csv', 'r+')
except FileNotFoundError:
    file = open('database.csv', 'w+')

writer = _csv.writer(file, delimiter=';')
reader = _csv.reader(file, delimiter=';')

id_to_person = {}
last_name_to_id = {}
first_name_to_id = {}
patronymic_to_id = {}
phone_number_to_id = {}
date_of_birth_to_id = {}


def print_line():
    print("---------------------------------------------------------------------")


def write_header():
    writer.writerow(["Id", "Last Name", "First Name", "Patronymic", "Date of Birth", "Phone Number"])


def check_for_birthday(p):
    date = p.date_of_birth
    now = datetime.datetime.now()
    date = datetime.datetime(year=now.year, month=date.month, day=date.day)
    now = datetime.datetime(year=now.year, month=now.month, day=now.day)
    if now > date:
        date = datetime.datetime(year=date.year + 1, month=date.month, day=date.day)
    ost = (date - now).days
    if ost < 14:
        print_line()
        print("REMINDER: " + p.fio.last_name + " " + p.fio.first_name +
              " " + p.fio.patronymic + " has a birthday in " + str(ost) + " days")


def check_for_date(date):
    try:
        date = datetime.datetime.strptime(date, "%d.%m.%Y")
        return date
    except ValueError:
        return None


def input_and_check_date():
    i = 0
    while i < 2:
        date = check_for_date(input())
        if date is not None:
            return date
        else:
            print("WRONG INPUT")
            if i == 0:
                print("Try again:")
            else:
                print("FAILED")
        i += 1
    return None


def check_for_reg(reg, str_to_check):
    pattern = re.compile(reg, flags=re.I | re.X)
    return check_for_pattern(pattern, str_to_check)


def check_for_pattern(pattern, str_to_check):
    if pattern.fullmatch(str_to_check) is not None:
        return str_to_check
    else:
        return None


def input_and_check_usual(reg: str) -> str:
    i = 0
    pattern = re.compile(reg, flags=re.I | re.X)
    while i < 2:
        inp = check_for_pattern(pattern, str(input()))
        if inp is None:
            print("WRONG INPUT")
            if i == 0:
                print("Try again:")
            else:
                print("FAILED")
        else:
            return inp
        i += 1
    return None


def check_person_from_file(id_, ln, fn, p, db, pn):
    id_ = check_for_reg("[0-9]+", str(id_))
    id_ = int(id_)
    ln = check_for_reg("([A-Z]+ (- [A-Z]+)*) | ([А-Я]+ (- [А-Я]+)*)", ln)
    fn = check_for_reg("([A-Z]+) | ([А-Я]+)", fn)
    p = check_for_reg("([A-Z]+) | ([А-Я]+) | ()", p)
    db = check_for_date(db)
    pn = check_for_reg("[+]?[0-9]+", pn)
    if id_ is not None and ln is not None and fn is not None and p is not None and db is not None and pn is not None:
        return Person(id_, Fio(ln, fn, p), db, pn)
    else:
        print("Database was corrupted!")
        print("Clear it or fix it and launch the application again")
        file.close()
        sys.exit(1)


def add_value_to_list(list_, key, value):
    if list_.get(key) is None:
        list_[key] = [value]
    else:
        list_[key] += [value]


def add_person_to_dictionaries(p):
    id_to_person[p.id] = p
    add_value_to_list(last_name_to_id, p.fio.last_name, p.id)
    add_value_to_list(first_name_to_id, p.fio.first_name, p.id)
    add_value_to_list(patronymic_to_id, p.fio.patronymic, p.id)
    add_value_to_list(phone_number_to_id, p.phone_number, p.id)
    add_value_to_list(date_of_birth_to_id, p.date_of_birth, p.id)


def add_one_line_from_file(line):
    global biggest_id

    line = line.rstrip()
    mas = line.split(';')
    p = check_person_from_file(mas[0], mas[1], mas[2], mas[3], mas[4], mas[5])
    if p.id >= biggest_id:
        biggest_id = p.id + 1
    add_person_to_dictionaries(p)
    check_for_birthday(p)


def before_start():
    if os.stat(file.name).st_size != 0:
        lines = file.readlines()
        i = 1
        while i < len(lines):
            add_one_line_from_file(lines[i])
            i += 1
    else:
        write_header()
    i = 0
    while i < biggest_id:
        if i not in id_to_person.keys():
            bisect.insort(freed_id, i)
        i += 1


def refresh():
    global is_up_to_date
    global biggest_id

    if is_up_to_date == 0:
        file.seek(0)
        file.truncate()
        write_header()
        new_biggest_id = 0

        for i in id_to_person.keys():
            p = id_to_person[i]
            writer.writerow(p.to_list())
            if new_biggest_id <= i:
                new_biggest_id = i + 1
        file.flush()
        biggest_id = new_biggest_id
        i = len(freed_id) - 1
        while i != -1 and freed_id[i] >= biggest_id:
            freed_id.pop(i)
            i -= 1
    is_up_to_date = 1


def clear():
    global freed_id
    global id_to_person
    global phone_number_to_id
    global date_of_birth_to_id
    global last_name_to_id
    global first_name_to_id
    global patronymic_to_id
    global is_up_to_date

    for i in id_to_person.keys():
        bisect.insort(freed_id, i)

    is_up_to_date = 0

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
    global freed_id
    global is_up_to_date

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
        bisect.insort(freed_id, id_to_delete)
        print("Person was deleted")

        is_up_to_date = 0
    else:
        print("Deletion was canceled")


def action(list_id, field, act_):
    n = len(list_id)
    if n > 0:
        n = len(list_id)
        more_than_1 = n > 1
        if more_than_1:
            print("There are " + str(n) + " persons with this " + field)
            i = 0
            while i < n:
                print(id_to_person[list_id[i]].to_str())
                i += 1

        if act_ == "d":
            if more_than_1:
                print("Choose what to delete --> print id")
                print("Cancel deletion       --> c")
                inp = input()
                if inp == "c":
                    return
                else:
                    delete(int(inp))
            else:
                delete(list_id[0])
    if n == 0:
        print("There is no person with this " + field)


def check_for_containing(all_list, key):
    if key in all_list.keys():
        list_id = all_list[key]
        return list_id
    else:
        print("There is no such person")
        return None


def action_launcher(key, all_list, name_of_list, type_of_action):
    list_id = check_for_containing(all_list, key)
    if list_id is not None:
        action(list_id, name_of_list, type_of_action)


def act_by_id(id_, type_of_action):
    try:
        str_ = id_to_person[id_].to_str()
        if type_of_action == "d":
            delete(id_)
        else:
            print("Here is your person:")
            print(str_)
    except KeyError:
        print("There is no such person")


def to_standard(inp: str):
    if len(inp) == 0:
        return inp
    else:
        inp = inp.lower()
        ch = inp[0].upper()
        inp = ch + inp[1:]
        return inp


def printing_choice(type_of_action):
    print("Last Name       --> print ln")
    print("First Name      --> print fn")
    print("Patronymic      --> print p")
    print("Date of Birth   --> print db")
    print("Phone Number    --> print pn")
    print("Id              --> print id")
    print("Go back         --> print b")
    inp = input()
    inp = inp.lower()
    message = "WRONG INPUT\nTry again:"
    if inp == "ln":
        print("Enter last name: ")
        last_name = input_and_check_usual("([A-Z]+ (- [A-Z]+)*) | ([А-Я]+ (- [А-Я]+)*)")
        if last_name is None:
            return
        action_launcher(to_standard(last_name), last_name_to_id, "last name", type_of_action)
    elif inp == "fn":
        print("Enter first name:")
        first_name = input_and_check_usual("([A-Z]+) | ([А-Я]+)")
        if first_name is None:
            return
        action_launcher(to_standard(first_name), first_name_to_id, "first name", type_of_action)
    elif inp == "p":
        print("Enter patronymic:")
        patronymic = input_and_check_usual("([A-Z]+) | ([А-Я]+) | ()")
        if patronymic is None:
            return
        action_launcher(to_standard(patronymic), patronymic_to_id, "patronymic", type_of_action)
    elif inp == "db":
        print("Enter date of birth (dd.mm.yyyy):")
        date_of_birth = input_and_check_date()
        if date_of_birth is None:
            print(message)
            return
        action_launcher(date_of_birth, date_of_birth_to_id, "date of birth", type_of_action)
    elif inp == "pn":
        print("Enter phone number")
        phone_number = input_and_check_usual("[+]?[0-9]+")
        if inp is None:
            return
        action_launcher(phone_number, phone_number_to_id, "phone number", type_of_action)
    elif inp == "id":
        print("Enter Id")
        id_ = input_and_check_usual("[0-9]+")
        act_by_id(int(id_), type_of_action)
    elif inp != "b":
        print("WRONG INPUT")


def input_person():
    global biggest_id
    global is_up_to_date
    print("Last Name:")
    ln = input_and_check_usual("([A-Z]+ (- [A-Z]+)*) | ([А-Я]+ (- [А-Я]+)*)")
    if ln is None:
        return
    ln = to_standard(ln)

    print("First Name:")
    fn = input_and_check_usual("([A-Z]+) | ([А-Я]+)")
    if fn is None:
        return
    fn = to_standard(fn)

    print("Patronymic:")
    p = input_and_check_usual("([A-Z]+) | ([А-Я]+) | ()")
    if p is None:
        return
    p = to_standard(p)

    print("Date of Birth (dd.mm.yyyy):")
    db = input_and_check_date()
    if db is None:
        return

    print("Phone Number:")
    pn = input_and_check_usual("[+]?[0-9]+")
    if pn is None:
        return

    if len(freed_id) > 0:
        id_ = freed_id[0]
        freed_id.pop(0)
    else:
        id_ = biggest_id
        biggest_id += 1

    add_person_to_dictionaries(Person(id_, Fio(ln, fn, p), db, pn))
    is_up_to_date = 0


def start():
    while 1:
        print_line()
        print("Add a person        --> print A(a)")
        print("Delete a person     --> print D(d)")
        print("Find a person       --> print F(f)")
        print("Clear database      --> print C(c)")
        print("Refresh table       --> print R(r)")
        print("Check if up-to-date --> print CH(ch)")
        print("Exit                --> print E(e)")

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
            clear()
            print("Base was cleared")
        elif inp == "e":
            refresh()
            file.close()
            return
        elif inp == "r":
            refresh()
        elif inp == "ch":
            print("Base " + ("is" if is_up_to_date else "MAY NOT be") + " up-to-date")
        else:
            print("No such command")


before_start()
start()