import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_product_urls(base_url, product_name):
    # Extract product URLs 
    product_urls = []
    page_number = 1
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

    while True:
        # URL of the overview page
        url = f"{base_url}/{product_name}/filter?pagina={page_number}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        product_containers = soup.find_all('div', class_='h3 mt--4@sm')

        if not product_containers:
            break

        for product_container in product_containers:
            product_url = base_url + product_container.find('a')['href']
            product_urls.append(product_url)

        page_number += 1
        
    return product_urls


def get_product_specifications(product_url, specifications):
    specs_dict = {}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract product name
    name_element = soup.find_all('h1', class_='js-product-name')  
    product_name = name_element[0].get_text(strip=True)
    specs_dict['product_name'] = product_name	

    # Extract sales price
    sales_price_element = soup.find("strong", {"class": "sales-price__current js-sales-price-current"})
    if sales_price_element:
        sales_price = sales_price_element.text.strip()
        specs_dict['sales_price'] = sales_price
    else:
        print(f"Sales price not found for product: {product_name}")   

    # Extract product specifications
    for specification in specifications:
        element = soup.find("dl", {"data-property-name": specification})
        if element:
            value = element.get("data-property-value", "").strip()
            specs_dict[specification] = value
        else:
            print(f"{specification} not found for product: {product_name}")

    return specs_dict       


if __name__ == "__main__":
    base_url = "https://www.coolblue.nl"
    product_name = "wasmachines"

    print('Extracting product URLs...')
    product_urls = get_product_urls(base_url, product_name)
    print(f'Found {len(product_urls)} products')

    specifications = ['Merk', 'Vulgewicht', 'Duur wascyclus', 'Restvochtpercentage',
                      'Energieklasse', 'Energieverbruik per jaar', 'Waterverbruik per jaar']

    print('Fetching specifications...')
    all_products = []
    for product_url in product_urls:
        specs = get_product_specifications(product_url, specifications)

        all_products.append(specs)
    
    df = pd.DataFrame(all_products)
    today = datetime.today().strftime('%Y%m%d')
    df.to_csv(f'data/coolblue_{product_name}_{today}.csv', index=False)
