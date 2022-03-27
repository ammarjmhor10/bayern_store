
import requests
from lxml import html
import json
from bs4 import BeautifulSoup


def get_prdouct_info_from_url(url):
    headers = {
    'authority': 'fcbayern.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
    }

    response = requests.get(url, headers=headers)
    html_code = response.text
    source = html.fromstring(html_code)
    json_data = source.xpath('//script[@id="wsProductDTO"]/text()')[0]
    product_info_scraped = json.loads(json_data)
    soup = BeautifulSoup(response.text,"lxml")
    catogery_fanshop = soup.find_all('a',class_='breadcrumbs__itemLink')[-1].get('href')
    try:
                size = [s['label'] for s in product_info_scraped['sizes']]
    except:
                size = 'no sizes'
    if product_info_scraped['allowedZones'] == []:
        if product_info_scraped['isArchivedProduct'] == False:
            product_info_edited = {
            'name' : product_info_scraped['name'],
            'sku number':product_info_scraped['code'],
            'price' : product_info_scraped['price'],
            'disc' : BeautifulSoup(product_info_scraped['description'], "lxml").text,
            'images': [i['product-l']['url'] for i in product_info_scraped['images']],
            'cat': catogery_fanshop,
            'sizes':size,
            'stock':'Available',
            'url':url  
            }
    return product_info_edited,product_info_scraped



#translate the sizes 
def get_label_sizes_arabic(label:dict):
    
    status = label['availability']['label']
    label_arabic = {
        'Available immediately': 'متاح فورا',
        'Sold out': 'انتهت الكمية',
        'Expected delivery from':'متوقع توصل الشحنة في ' ,
        'Only': 'متوفر فقط '
    }
    if status not in label_arabic and 'Only' not in status:
        soup = BeautifulSoup(status,'lxml').find('p').text
        araibc_time = soup.replace('Expected delivery from',label_arabic['Expected delivery from'])
        return araibc_time
    if 'Only' in status:
        only = str(label_arabic['Only']) + ' '+ str(''.join(filter(str.isdigit,status)))
        return only
    
    
    return  label_arabic.get(status)


def get_size_info(product_info_scraped):
    if product_info_scraped['isArchivedProduct'] == False:
        label = [get_label_sizes_arabic(var) for var in product_info_scraped['variants'] ]
        sku_size = [pur['code'] for pur in product_info_scraped['variants'] if pur['price'] == product_info_scraped['price'] ]
        siz = [s['label'] for s in product_info_scraped['sizes']]
        vari = dict(zip(siz,label))    
        values = [{'name':str(vari.get(d)+ ' -- '+ d)} for (k,d) in enumerate(vari)]
        return values

    else:
        return "delete"

# print(get_label('Expected delivery from 02.05.2022'))






# print(''.join(filter(str.isdigit,'jsh 23')))
# html_code = get_prdouct_info_from_url('https://fcbayern.com/shop/en/street-socks/26491/')
# print(html_code)
# x_json = get_json_from_html(html_code)
# print(x_json)
# values = get_x_dict(x_json)
# print(values)