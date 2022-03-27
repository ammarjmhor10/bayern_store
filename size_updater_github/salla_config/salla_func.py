import requests
import json
import os 
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate
import six
load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get('GOOGLE_TRANS')


#get data from salla
def get_url_fCB(part):
    url = f'https://api.salla.dev/admin/v2/{part}'
    headers ={'authorization': 'Bearer ' + os.environ.get("SALLA_API_TOKEN") }
    r = requests.get(url, headers=headers)
    data = r.json()
    return data

def delete_url_fCB(part):
    url = f'https://api.salla.dev/admin/v2/{part}'
    headers ={'authorization': 'Bearer ' + os.environ.get("SALLA_API_TOKEN") }
    r = requests.delete(url, headers=headers)
    data = r.json()
    return data

#this is updating sizes to latest 
def update_sizes(sku:int,info:list):
    url = f'https://api.salla.dev/admin/v2/products/' + str(sku) + 'options'
    headers ={'authorization': 'Bearer ' +  os.environ.get("SALLA_API_TOKEN") }
    option_json ={
            "name": "المقاس",
            "display_type": "text",
            "values": info
            }
    r = requests.put(url, headers=headers,json=option_json)
    data = r.json()
    return data


#this is updating sizes to latest 
def create_or_update_sizes(product_id:int,info:list):
    url = f'https://api.salla.dev/admin/v2/products/' + str(product_id) + '/options'
    headers ={'authorization': 'Bearer ' +  os.environ.get("SALLA_API_TOKEN") }
    option_json ={
            "name": "المقاس",
            "display_type": "text",
            "values": info
            }
    r = requests.post(url, headers=headers,json=option_json)
    data = r.json()
    return data
def put_url(part:str,info:dict):
    url = f'https://api.salla.dev/admin/v2/{part}'
    headers ={'authorization': 'Bearer ' + os.environ.get("SALLA_API_TOKEN") }
    r = requests.put(url, headers=headers,json=info)
    data = r.json()
    return data


#hide the product if it is not available 
def sold_out_products(product:dict,sku:int):
    url = 'https://api.salla.dev/admin/v2/products/sku/' + str(sku)
    headers ={'authorization': 'Bearer ' + os.environ.get("SALLA_API_TOKEN") }
    data_item = {
        'name':product['name'],
        'price':product['price']['amount'],
        "categories": [
                        2040876110
                    ]
    }
    r = requests.put(url, headers=headers,json=data_item)
    data = r.json()
    return data['data']

#send json info and create product in salla
def create_product_salla(name,disc,price,sku,size1):
    url = 'https://api.salla.dev/admin/v2/products'
    headers ={'authorization': 'Bearer ' + os.environ.get("SALLA_API_TOKEN")}
    if size1 != 'no sizes':
        size = str(size1).replace("'",'  ')
        disc1 = disc + str(sku)
        data_item = {
            'name':name,
            'price':price,
            'product_type':'product',
            'description': disc1,
            'sku':sku,
            'require_shipping':1,
            'enable_note':1
        }
        r = requests.post(url, headers=headers,json=data_item)
        data = r.json()
        return [data['data']['urls']['customer'],data['data']['id']]
    else :
        data_item = {
            'name':name,
            'price':price,
            'product_type':'product',
            'description': disc,
            'sku':sku,
            'require_shipping':1,
            'enable_note':1
        }
        r = requests.post(url, headers=headers,json=data_item)
        data = r.json()
        #return the url store and product id
        return [data['data']['urls']['customer'],data['data']['id']]



def translate_text(text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """


    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language='ar')


    return result["translatedText"]



#price func 
def get_price_SAR_cloth(price):
    if price == 0.0:
        return 0
    tax = 0.15
    exhgange = 4.55
    shiping = 100
    discount = 0.256
    price_discout = price - (discount * price)
    price_SAR = (price_discout *exhgange)  
    price_tax = (price_SAR*tax)+price_SAR
    price_with_sh = price_tax + shiping
    
    return (10 * ((price_with_sh + 5) // 10)) - 1



# translate and create product in salla
def upload_product_to_salla(product_info:dict):
    #start translate name and discription of the product 
    trans_name = translate_text(product_info['name'])
    trans_disc = translate_text(product_info['disc'])
    #set price in SR 
    price_conv = get_price_SAR_cloth(product_info['price'])
    #set product code
    sku = product_info['sku number']
    #set sizes labels and type 
    sizes1 = str(product_info['sizes'])
    #create product
    creat_proudct = create_product_salla(trans_name,trans_disc,price_conv,sku,sizes1)
    return creat_proudct

#download image url and safe it in the folder 
def upload_image_home(url_image,sku,count_images):
    headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    #name the image file with sku 
    name_image =   str(sku) +  '_' + str(count_images) + '.png'
    #get the image url and downlaod with the name file and return the name to upload it 
    with open(name_image, 'wb') as f:
            image = requests.get(url_image,headers=headers).content
            f.write(image)
            f.close()
    return name_image 


#upload image to the store with product id 
def upload_images_to_salla(id_item:int,image:str,sku:int,count_images):
    #url for images in salla with product id
    url = f"https://api.salla.dev/admin/v2/products/{id_item}/images"
    
    image_file = upload_image_home(image,sku,count_images)
    msg = "IMAGES ARE UPLOADING .. " 
    payload={}
    files=[
    ('photo',(image_file ,open(image_file,'rb'),'image/png'))
    ]
    headers = {
    'Authorization': 'Bearer ' + os.environ.get("SALLA_API_TOKEN")
    }
    #send the image 
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    #delete the image 
    os.remove(image_file)
    



#TEST CODE : 


        #get the products info and option id 
        # products_info_id = get_url_fCB('/products/sku/27739')['data']
        # print(products_info_id)
        # opt_info_id = products_info_id['id'] 
        # opt_id = products_info_id['options'][0]
        # #delete old option
        # delete_url_fCB('/products/options/'+str(opt_id))
        # #create new option
        # create_new_opt = post_url('/products/'+ str(opt_info_id) + '/options',)


        # product = get_url_fCB('products/sku/27563')['data']

        # # print(product)
        # print(update_products_url(product,27563))