import requests
from bs4 import BeautifulSoup
import pandas as pd



def page_scraping(url, model, mileage, price, dealer, dealer_rating, car_url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all('div', {'class': 'vehicle-card'})

    for item in results:
        model.append(item.find('h2').text)
        mileage.append(item.find('div', {'class': 'mileage'}).text)
        price.append(item.find('span',  {'class': 'primary-price'}).text)
        dealer.append(item.find('strong').text)
        dealer_rating.append(item.find('span',  {'class': 'sds-rating__count'}).text) if item.find('span',  {'class': 'sds-rating__count'}) else dealer_rating.append('-1')
        car_url.append(item.find('a',  {'class': 'vehicle-card-link js-gallery-click-link'})['href'])

    return model, mileage, price, dealer, dealer_rating, car_url


def multi_page_scraping(brands, n):
    model, mileage, price, dealer, dealer_rating, car_url = [], [], [], [], [], []
    for brand in brands:
        for i in range(1, n+1):
            url = f'https://www.cars.com/shopping/results/?list_price_max=&makes[]={brand}&maximum_distance=all&models[]=&page={i}&stock_type=cpo&zip=48108'
            model, mileage, price, dealer, dealer_rating, car_url = page_scraping(url, model, mileage, price, dealer, dealer_rating, car_url)
            # print(len(model), len(mileage), len(price), len(dealer), len(dealer_rating), len(car_url))
    listed_cars = pd.DataFrame({'model':model, 'mileage':mileage, 'price': price, 'dealer':dealer, 'dealer Rating': dealer_rating, 'url': car_url})
    listed_cars.to_json('file.json')
    return listed_cars

def main():
    brands = ['cadillac']
    n = 2
    listed_cars = multi_page_scraping(brands, n)
    
    print(listed_cars)

if __name__ == '__main__':

    main()
