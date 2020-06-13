# -*- coding: utf-8 -*-
import random
import string
import datetime
import json  # Подключаем библиотеку для преобразования данных в формат JSON
import socket
import os # Подключаем библиотеку для работы с функциями операционной системы (для проверки файла)
import pymongo
from bson.json_util import dumps, loads
from bson import json_util
import win32event
import win32api
import win32file
from winerror import ERROR_ALREADY_EXISTS
from sys import exit
import threading
from flask import Flask, request, render_template, flash, redirect, json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_pymongo import PyMongo
import requests

# mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
# dblist = mongoclient.list_database_names()


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Typography"
mongo = PyMongo(app)

def check_token(token):
    chekingToken = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))    
    col = mongo.db["Persons"].find_one({"Token":str(token)})
    if token == "":
        return False
    else:
        if col:
            chekingToken = col["Token"]
            if chekingToken == token:
                return True
            else: 
                return False
        else:
            return False

@app.route("/add_order",  methods=['POST'])
def add_order():
    add_operation_in_journal('add_order')
    token = str(request.form["ClientToken"])    
    if check_token(token):
        user = mongo.db["Persons"].find_one({"Token":token})
        neworder = {}
        ServiceID = int(request.form['ServiceID'])
        Count = int(request.form["Count"])
        ClientID = int(user["_id"])
        neworder["_id"] = (get_max_id("Orders")) + 1
        neworder["Client"] = find_by_id(ClientID, "Persons")
        neworder["Service"] = find_by_id(ServiceID, "Services")
        neworder["Count"] = Count
        neworder["Date"] = datetime.datetime.now()
        neworder["State"] = "В обработке"
        mongo.db["Orders"].save(neworder)
        return "Заказ был добавлен"
    else:
        return "Неверный токен"

@app.route("/add_chatmessage", methods=['POST'])
def add_chatmessage():
    add_operation_in_journal('add_chatmessage')
    token = str(request.form["ClientToken"])    
    if check_token(token):
        user = mongo.db["Persons"].find_one({"Token":token})
        OrderID = int(request.form["OrderID"])
        Message = request.form["Message"]
        newchatmessage = {}
        newchatmessage["_id"] = (get_max_id("ChatMessages")) + 1
        newchatmessage["Author"] = user
        newchatmessage["Order"] = find_by_id(OrderID, "Orders")
        newchatmessage["Message"] = Message
        newchatmessage["Date"] = datetime.datetime.now()
        mongo.db["ChatMessages"].save(newchatmessage)
        return "Сообщение было отправлено в заказ"
    else:
        return "Неверный токен"

def find_by_id(id, collection):
    col = mongo.db[collection]
    obj = {}
    for x in col.find():
        if x["_id"] == id:
            obj = x
    return obj

@app.route("/read_order", methods=['GET'])            
def read_order():
    add_operation_in_journal('read_order')
    token = str(request.headers["userToken"])
    if check_token(token):
        orderID = int(request.headers["OrderID"])
        x = mongo.db["Orders"].find_one({"_id":orderID})
        content = dumps(x, default = myconverter)
        return content

def user_auth(login, password):
    col = mongo.db["Persons"]
    for x in col.find():
        if x["Login"] == login and x["Password"] == password:
            return True
        else:
            return False

@app.route("/read_services")
def read_services(): # Считываем список книг
    add_operation_in_journal('read_services')
    col = mongo.db["Services"]
    for x in col.find():
        print(x)
    cursor = col.find()
    content = dumps(cursor)
    return content

@app.route("/read_sales")
def read_sales():
    add_operation_in_journal('read_sales')
    col = mongo.db["Sales"]
    for x in col.find():
        print(x)
    cursor = col.find()
    content = dumps(cursor, default = myconverter)
    return content

@app.route("/read_orders", methods=['GET'])
def read_orders():
    add_operation_in_journal('read_orders')
    token = str(request.headers["userToken"])
    if check_token(token):
        user = mongo.db["Persons"].find_one({"Token":token})
        col = mongo.db["Orders"]
        for x in col.find({"Client._id":user["_id"]}):
            print(x)
        cursor = col.find({"Client._id":user["_id"]})
        content = dumps(cursor, default = myconverter)
        return content
    else:
        return "Неверный токен"


@app.route("/read_orders_by_date", methods=['GET'])
def read_orders_by_date():
    add_operation_in_journal('read_orders_by_date')
    token = str(request.headers["Token"])    
    if check_token(token):
        user = mongo.db["Persons"].find_one({"Token":token})
        stringdatestart = request.headers["StartDate"]
        stringdateend = request.headers["EndDate"]
        date1 = stringdatestart.split(',')
        date2 = stringdateend.split(',')
        from_date = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]))
        to_date = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]))
        cursor = mongo.db["Orders"].find({"Date": {"$gte": from_date, "$lt": to_date}, "Client._id":user["_id"]})
        content = dumps(cursor, default = myconverter)
        return content

@app.route("/read_chatmessages", methods=['GET'])
def read_chatmessages():
    add_operation_in_journal('read_chatmessages')
    token = str(request.headers["userToken"])    
    if check_token(token):
        user = mongo.db["Persons"].find_one({"Token":token})
        orderID = int(request.headers["orderID"])
        col = mongo.db["ChatMessages"]
        for x in col.find({"Order._id":orderID}):
            print(x)
        cursor = col.find({"Order._id":orderID})
        content = dumps(cursor)
        return content

def get_max_id(collection):
    col = mongo.db[collection]
    maxid = 1
    for x in col.find().sort("_id"):
        maxid = x["_id"]
    return maxid


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

@app.route("/authorization", methods=['POST'])
def authorization():
    add_operation_in_journal('authorization')
    login = request.form['login']
    password = request.form["password"]
    if user_auth(login, password) == True:
        print("Попытка авторизоваться прошла успешно")
        token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
        x = mongo.db["Persons"].find_one({"Login":login, "Password":password})
        x["Token"] = token
        x["TokenDate"] = datetime.datetime.now()
        mongo.db["Persons"].save(x)
        return token
    else: 
        return "Ошибка авторизации"

@app.route("/logout", methods=['POST'])
def logout():
    add_operation_in_journal('logout')
    token = str(request.form['Token'])
    x = mongo.db["Persons"].find_one({"Token":token})
    x["Token"] = None
    x["TokenDate"] = None                
    mongo.db["Persons"].save(x)
    return "Выход был произведен успешно!"

@app.route("/changepass", methods=['POST'])
def changepass():
    add_operation_in_journal('changepass')
    token = str(request.form['Token'])
    password = request.form['Password']    
    if check_token(token):            
            x = mongo.db["Persons"].find_one({"Token":token})              
            x["Password"] = password
            mongo.db["Persons"].save(x)
            print("Попытка смены пароля прошла успешно ")
            return "Ваш пароль был успешно изменён"

class FileMutex:
    def __init__(self):
        self.mutexname = "typography_filemutex"

        self.mutex = win32event.CreateMutex(None, 1, self.mutexname)
        self.lasterror = win32api.GetLastError()
    
    def release(self):
        return win32event.ReleaseMutex(self.mutex)

mutex = FileMutex()
mutex.release()

def add_operation_in_journal(opeartion):
    import time
    mutex = FileMutex()
    date=datetime.datetime.now()
    date = str(date)
    row = str(opeartion) + "=====" + str(date) + '\n'
    while True:
        res = win32event.WaitForSingleObject(mutex.mutex, win32event.INFINITE )      
        f = open('journalflask.txt', 'a')
        f.write(row)
        f.close()
        mutex.release()
        return

class singleinstance:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexname = "testmutex_{b5123b4b-e59c-4ec7-a912-51be8ebd5819}" #GUID сгенерирован онлайн генератором
        self.mutex = win32event.CreateMutex(None, False, self.mutexname)
        self.lasterror = win32api.GetLastError()
    
    def aleradyrunning(self):
        return (self.lasterror == ERROR_ALREADY_EXISTS)
        
    def __del__(self):
        if self.mutex:
            win32api.CloseHandle(self.mutex)


from sys import exit
myapp = singleinstance()


if myapp.aleradyrunning():
    print("Another instance of this program is already running")
    exit(0)

if __name__ == '__main__':
    app.run()
