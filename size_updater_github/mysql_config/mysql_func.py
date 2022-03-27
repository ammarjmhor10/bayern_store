import mysql.connector
from soupsieve import bs4
import os 
from dotenv import load_dotenv
load_dotenv()


mydb = mysql.connector.connect(
  host=os.environ.get('HOST'),
  user=os.environ.get('USERNAME'),
  password=os.environ.get('PASSWORD'),
  database=os.environ.get('DATABASE')
)


def get_sku():
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("""SELECT sku_number FROM products_live""")
    sku_list = [sku[0] for sku in mycursor.fetchall()]
    return sku_list


def get_url_from_sku(sku):
    values = sku
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("""SELECT url FROM products_all where sku_number=%s """,(sku,))
    url = mycursor.fetchone()
    return url[0]




