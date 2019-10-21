"""This module is to configure app to connect with database."""

from pymongo import MongoClient

DATABASE = MongoClient()['doubtnut'] # DB_NAME
DEBUG = True
# client = MongoClient('mongodb://doubtnut:Doubtnut_2018@13.233.54.212:27017/')
client = MongoClient('13.233.54.212', 27017)


# mongodb://13.233.54.212:27017/doubtnut