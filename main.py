from collections import UserDict
from datetime import datetime
import pickle


file_name = "contact_book.bin"

def input_error(func):
    def Inner(*args):
        try:
            res = func(*args)
        except KeyError:
            print("Use valid contact!")
            exit()
        except ValueError:
            print("Write valid phone number")
            exit()
        except TypeError:
            return "Use valid task!"
        else:
            return res
    return Inner

class Field:
    def __init__(self, value = None):
        self._value = value

    def __str__(self):
        return str(self._value)

class Name(Field):
    def get_name(self):
        return self._value

    def set_name(self, new_value):
        self._value = new_value

    value = property(get_name, set_name)

class Phone(Field):
    def get_phone(self):
        return self._value

    def set_phone(self, new_value):
        if len(new_value) == 10 and new_value.isdigit():
            self._value = new_value
            pass
        else:
            print("Use valid phone format.")
            
    value = property(get_phone, set_phone)            
            
class Birthday(Field):
    def get_bday(self):
        return str(self._value.date())

    def set_bday(self, new_value):
        try:
            self._value = datetime.strptime(new_value, "%d.%m.%Y")
        except ValueError:
            print("Use birthday format dd.mm.yyyy!")
            exit()
            
    value = property(get_bday, set_bday)
    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone = None, birthday = None):
        p = Phone()
        p.value = phone
        if p.value is not None:
            self.phone = p
            self.phones.append(self.phone)
        if birthday:
            b = Birthday()
            b.value = birthday
            self.birthday = b
            
    def days_to_birthday(self):
        today_date = datetime.now()
        contact_bd = datetime.strptime(self.birthday.value, "%Y-%m-%d").replace(year=today_date.year)
        if today_date.date() > contact_bd.date():
            res = contact_bd.replace(year=today_date.year + 1).date() - today_date.date()
        else:
            res = contact_bd.replace(year=today_date.year).date() - today_date.date()
            
        return f"{res.days} days until {self.name}'s birthday."
    
    @input_error    
    def edit_phone(self, old_phone, new_phone):
        new_list = [p.value for p in self.phones] 
        old_phone_indx = new_list.index(old_phone)
        new_list.remove(old_phone)
        p = Phone()
        p.value = new_phone
        self.phone = p
        if p.value is not None:
            self.phones.pop(old_phone_indx)
            self.phones.insert(old_phone_indx, self.phone)
        
    def find_phone(self, phone):
        new_list = [p.value for p in self.phones]
        try:
            p_indx = new_list.index(phone)
        except ValueError:
            print("This contact doesn't have such a phone.")
            exit()
        return self.phones[p_indx]
    
    @input_error        
    def remove_phone(self, phone):
        new_list = [p.value for p in self.phones] 
        phone_indx = new_list.index(phone)
        self.phones.pop(phone_indx)

    def __str__(self):
        if self.birthday and self.phones:
            return (f"Contact name: {self.name.value}, "
                    f"phones: {'; '.join(p.value for p in self.phones)}, "
                    f"birthday: {self.birthday.value}")
        elif self.phones:
            return (f"Contact name: {self.name.value}, "
                    f"phones: {'; '.join(p.value for p in self.phones)}")
        else:
            return f"Contact name: {self.name.value}"

class AddressBook(UserDict):
    try:
        with open (file_name, "rb+") as fh:
            unpacked = pickle.load(fh)
            def __init__(self):
                self.data = AddressBook.unpacked
    except FileNotFoundError:
        ...
        
    def save_file(self):
        with open (file_name, "wb") as fh:
            pickle.dump(self.data, fh)
        
    def add_record(self, record):
        self.data[record.name.value] = record
    
    @input_error    
    def find(self, name):
        for k in self.data.keys():
            if k == name:
                return self.data[k]
        print("There is no such contact in the address book")
        
    def search(self, val):
        for v in self.data.values():
            phones = [str(p) for p in v.phones]
            if val in str(v.name) or val in "".join(phones):
                print(v)

    @input_error
    def delete(self, name):        
        self.data.pop(name)

    @input_error
    def iterator(self, n_on_page):
        list_notes = []
        for v in self.data.values():
            if v.birthday:
                new_v = f"Contact name: {v.name.value}, "
                f"phones: {'; '.join(p.value for p in v.phones)}, "
                f"birthday: {v.birthday.value}"
            else:
                new_v = f"Contact name: {v.name.value}, "
                f"phones: {'; '.join(p.value for p in v.phones)}"
            list_notes.append(new_v) 
            if len(list_notes) == n_on_page:
                yield list_notes
                list_notes = []
 
def add_func(task):
    rec = Record(task[0])
    rec.add_phone(*task[1:])
    book.add_record(rec)

@input_error 
def change_func(task):
    rec = book.find(task[0])
    rec.edit_phone(task[1], task[2])    
        
@input_error 
def phone_func(task):
    rec = book.find(task[0])
    return rec.phones

@input_error 
def show_func(task):
    lst = []
    for record in book.data.values():
        lst.append(record)
    return lst

@input_error 
def exit_func(task):
    print("Good bye!")
    exit()    

func = {add_func: ["add", "+"], change_func: ["change", "edit"], phone_func: ["phone"], 
        show_func: ["show", "show all"], exit_func: ["exit", "good", "bye", "close"]}

@input_error 
def get_func(task):
    for k, v in func.items():
        if task in v:
            return k
        
dict_contacts = {}

@input_error        
def task_handler(task):
    task = task.lower()
    
    if task == "hello":
        return "How can I help You?"
    
    task_list = task.split()
    
    handler = get_func(task_list[0])
    return handler(task_list[1:])

def main():
    global book
    book = AddressBook()
    while True:
        task = input(">>>")
        res = task_handler(task)
        
        if isinstance(res, list):
            for i in res:
                print(i)
        elif res:
            print(res)

if __name__ == "__main__":
    print(main())
                    
# # Створення нової адресної книги
# book = AddressBook()

# # Створення запису для John
# john_record = Record("John")
# john_record.add_phone("1234567890", "01.04.1998")
# john_record.add_phone("5555555555")

# print(john_record.days_to_birthday())

# # Додавання запису John до адресної книги
# book.add_record(john_record)

# # Створення та додавання нового запису для Jane
# jane_record = Record("Jane")
# jane_record.add_phone("9876543210")
# book.add_record(jane_record)

# # Виведення всіх записів у книзі
# for name, record in book.data.items():
#     print(record)

# # Знаходження та редагування телефону для John
# john = book.find("John")
# john.edit_phone("1234567890", "1112223333")

# print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

# # Пошук конкретного телефону у записі John
# found_phone = john.find_phone("5555555555")
# print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

# # Видалення запису Jane
# book.delete("Jane")