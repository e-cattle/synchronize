from pymongo import MongoClient
from .envs import URL_DB, DATABASE

client = MongoClient(URL_DB)

my_database = client[DATABASE]
