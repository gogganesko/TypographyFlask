import json
import requests
from os import system
from bson.json_util import dumps, loads
from bson import json_util
global URL

URL = 'http://127.0.0.1:5000'

def print_services(services): #вернулся список, на экран вывести список
    print("="*45)
    for service in services:
        print("%s - %s - %s Руб." % (service["_id"], service["Name"], service["Price"]))

def print_chat(ChatMessages):
    for message in ChatMessages:
        author = message["Author"]
        print("Автор:%s\nДата:%s\nСообщение:%s" %(author["Name"], message["Date"], message["Message"]))

def print_sales(sales):
    print("="*45)
    for sale in sales:
        print("%s - %s - %s - %s - %s" % (sale["_id"], sale["Name"], sale["DateStart"], sale["DateEnd"], sale["Percent"]))

def print_orders(orders):
    print('='*45)
    for order in orders:
        print("%s - %s" % (order["_id"], order["State"]))        

def print_order(order):
    print('='*45)
    client = order["Client"]
    service = order["Service"]
    print("ID:%s \nВладелец:%s \nУслуга:%s \nКоличество:%s \nСтатус:%s \n" %(order["_id"], client["Name"], service["Name"], order["Count"], order["State"]))

def print_orders_by_date(orders):
    print("="*45)
    for order in orders:
        print("%s - %s - %s" % (order["_id"], order["State"], order["Date"]))

def start_client(): # Основная функция, запускающая клиента. Эта функция вызывается в конце файла, после определения всех нужных деталей
    isauth = 0
    authuserid = 0
    currentuser = {}
    print ("Подключились к серверу")


    while True: # Бесконечный цикл работы с сервером

        print("Главное меню:")
        print("0 - Просмотреть список услуг")
        print("1 - Просмотреть список акций")
        if isauth == 1:
            print("2 - Сделать заказ")
        print("3 - Выйти из программы")
        if isauth == 1:
            print("4 - Просмотреть мои заказы")
        if isauth == 0:
            print("5 - Авторизоваться")
        else:
            print("6 - Выйти из профиля")
            print("7 - Забыли пароль|Смена пароля")
            print("8 - Отправить сообщение в чат заказа")
            print("9 - Подробная информация о заказе")
            print("10 - Просмотреть сообщения в чате заказа")
            print("11 - Поиск заказов по датам")
        task = input() # Считывание данных с клавиатуры

        if not task.isdigit() or int(task) > 20: # Если ввод пользователя содержит что-то кроме цифр 
            print ("Неправильная команда!")
            continue # В этом случае начинаем цикл заново, пусть пользователь заново вводит текст

        task=int(task) # Преобразовываем номер задачи в числовой формат

        if (task == 0):
            url = URL + '/read_services'            
            response = requests.get(url)
            services = loads(response.text)
            print_services(services)
            continue
        if (task == 1):
            url = URL + '/read_sales'            
            response = requests.get(url)
            sales = loads(response.text)
            print_sales(sales)
            continue
        if (task == 2):
            url = URL + '/read_services'            
            response = requests.get(url)
            services = loads(response.text)
            print_services(services)
            url = URL + '/add_order' 
            order = {}    
            order["ServiceID"] = int(input("Введите ID услуги:"))
            order["Count"] = input("Введите количество:")    
            order["ClientID"] = currentuser["_id"]
            response = requests.post(url, data=order)
            print(response.text)
        if (task == 3):
            exit(0)
        if (task == 4):
            url = URL + '/read_orders'
            response = requests.get(url, headers={'userID':str(currentuser["_id"]) })            
            orders = loads(response.text)
            print_orders(orders)
        if (task == 5):
            url = URL + '/authorization'
            login = str(input("Введите логин:\n"))
            password = str(input("Введите пароль:\n"))
            msg = {}
            msg["login"] = login
            msg["password"] = password
            response = requests.post(url, data=msg)
            if response.text == "Ошибка авторизации":
                print("Неправильный логин или пароль")
            else: 
                currentuser = loads(response.text)
                isauth = 1
                print("Вы авторизовались:" + currentuser["Name"])
        if (task == 6):
            url = URL + '/logout'
            msg = {}
            msg["UserID"] = currentuser["_id"]
            response = requests.post(url, data=msg)
            isauth = 0
            print(response.text)
        if (task == 7):
            url = URL + '/changepass'
            password = str(input("Введите новый пароль:"))
            msg = {}
            msg["Password"] = password
            msg["UserId"] = currentuser["_id"]
            response = requests.post(url, data=msg)
            print(response.text)
        if (task == 8):
            url = URL + '/read_orders'
            response = requests.get(url, headers={'userID':str(currentuser["_id"]) })            
            orders = loads(response.text)
            print_orders(orders)
            url = URL + "/add_chatmessage"
            chatmessage = {}
            chatmessage["OrderID"] = int(input("Введите ID заказа:"))
            chatmessage["Message"] = str(input("Введите текст сообщения:"))
            chatmessage["ClientID"] = currentuser["_id"]
            response = requests.post(url, data=chatmessage)
            print(response.text)
        if (task == 9):
            url = URL + '/read_orders'
            response = requests.get(url, headers={'userID':str(currentuser["_id"]) })            
            orders = loads(response.text)
            print_orders(orders)
            OrderID = int(input("Введите ID заказа:"))
            url = URL + "/read_order"
            response = requests.get(url, headers={'userID':str(currentuser["_id"]), 'OrderID':str(OrderID)})
            order = loads(response.text)
            print_order(order)
        if (task == 10):
            url = URL + '/read_orders'
            response = requests.get(url, headers={'userID':str(currentuser["_id"]) })            
            orders = loads(response.text)
            print_orders(orders)
            OrderID = int(input("Введите ID заказа:"))
            url = URL + '/read_chatmessages'
            response = requests.get(url, headers={'userID':str(currentuser["_id"]), 'orderID':str(OrderID)})
            chatmessage = loads(response.text)
            print_chat(chatmessage)
        if (task == 11):
            StartDate = str(input("Введите начальную дату для поиска в формате\nгггг,мм,дд:"))
            EndDate = str(input("Введите конечную дату для поиска в формате\nгггг,мм,дд:"))
            url = URL + '/read_orders_by_date'
            response = requests.get(url, headers={'userID':str(currentuser["_id"]), 'StartDate':StartDate, 'EndDate':EndDate})
            orders = loads(response.text)
            print_orders(orders)
start_client()

