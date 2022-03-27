from numpy import product
import telebot
from mysql_config import mysql_func as data 
from salla_config import salla_func as salla
from scraping import scraping_func as scrape
from flask import Flask , request
import threading
import os 
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
#token bot telegram
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))


#this is a large func 
#start getting skus number from databases
#scrape the data and get last sizes 
#uplaod the data to salla store 
#done
def update_size_products_from_database():
    sku_list = data.get_sku()
    for sku in sku_list:
        print(sku)
    #get the products info and option id 
        try:
            url_sku = data.get_url_from_sku(sku)
            product_scraped = scrape.get_prdouct_info_from_url(url_sku)
            values = scrape.get_size_info(product_scraped[1])
            products_info_id = salla.get_url_fCB('/products/sku/'+ str(sku))['data']
            if values != 'delete':
                opt_info_id = products_info_id['id'] 
                opt_id = products_info_id['options'][0]['id']
                #delete old option
                delete_option = salla.delete_url_fCB('/products/options/'+str(opt_id))
                if not delete_option['success']:
                    print('deleting error')
                #create new option
                create_new_opt = salla.create_or_update_sizes(str(opt_info_id) ,values)
            else :
                delete_product = salla.sold_out_products(products_info_id,sku)

        except Exception as e:
            print(sku,e,end='\n')
    return sku_list    


#this is endpoint to update the products sizes with threading background
@app.route('/update')
def get_update():
    threading.Thread(target=update_size_products_from_database).start()
    return "App started .. "




#commands info
cc = """



/fcb >> to upload link item



/Size >> to check for size available 

/update >> to update the products


"""




@bot.message_handler(commands=['start'])
def sen(mes):
    bot.send_message(mes.chat.id,cc)



fcb = """

SEND THE LINK'S PRODUCT ONLY PLEASE LIKE THIS LINK:

https://fcbayern.com/shop/en/hands-of-god-sweatshirt-gnabry/29579/

 """



@bot.message_handler(commands=['FCB'])
def sen_fcb(mes):
    bot.send_message(mes.chat.id,fcb)



@bot.message_handler(commands=['update'])
def sen_fcb(mes):
    bot.send_message(mes.chat.id,'update started ..')
    threading.Thread(target=update_size_products_from_database).start


#get the url func
def FCB(mes):
    if mes.text[8:20] == 'fcbayern.com':
        return True
    else:
        return False



def upload_from_bot(url,per):
    bot.send_message(per,'START  CHECKING FROM URL ....')
    product_data = scrape.get_prdouct_info_from_url(url)
    sku = product_data[0]['sku number']
    check_av = salla.get_url_fCB('products/sku/' + sku)
    if check_av['success']:
        bot.send_message(per,'the product availbale just search for sku number in the site please')
        bot.send_message(per,'sku number is ' + str(sku))
    # bot.send_message(per,"DATA COLCTING .... " + data['name'] + str(data['sizes']))
    else:
        data_sending = salla.upload_product_to_salla(product_data[0])
        get_sizes = scrape.get_size_info(product_data[1])
        create_sizes_product = salla.create_or_update_sizes(data_sending[1],get_sizes)
        print(create_sizes_product)
        print(data_sending)
        bot.send_message(per,'LOADING .. ')
        for img in range(len(product_data[0]['images'])):
            image = salla.upload_images_to_salla(str(data_sending[1]),product_data[0]['images'][img],product_data[0]['sku number'],img)
            bot.send_message(per,' IS LOADING .. ')
        bot.send_message(per,'DONE ')
        bot.send_message(per,data_sending[0])

#handle the url to upload product
@bot.message_handler(func=FCB)
def send_link_fcb(mes):

    per = mes.chat.id
    bot.send_message(per,'START  UPLOADING ....')
    threading.Thread(target=upload_from_bot(mes.text,mes.chat.id)).start
  





@app.route('/', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

#to set webhook and remove it
@app.route("/setwebhook",methods=["GET"])
def set_webhook():
    url_https = str(request.url_root).replace('http','https')
    bot.remove_webhook()
    bot.set_webhook(url=url_https)

    return "webhook is set!"


#remove webhook
@app.route("/removewebhook",methods=["GET"])
def remove_webhook():
    bot.remove_webhook()
    return "webhook is removed!"


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
  
