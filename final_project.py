import requests
from bs4 import BeautifulSoup
import pandas as pd
import os.path
from data_structure import build_tree
import json
def page_scraping(url, model, mileage, price, dealer, dealer_rating, car_url):
    '''
    This function is responsible for scraping data on a single page

    Parameters
    ---------------------
    url: the url of the page
        the url of the page
    model: str
        the model of the car: year, brand, model
    mileage: str
        the mileage of the car
    price: str
        the listed price of the car
    dealer: str
        the dealer name of the car
    dealer_rating: float
        the rating of the dealer
    car_url: str
        the url of each car

    Returns
    ----------------------
    url: the url of the page
        the url of the page
    model: str
        the model of the car: year, brand, model
    mileage: str
        the mileage of the car
    price: str
        the listed price of the car
    dealer: str
        the dealer name of the car
    dealer_rating: float
        the rating of the dealer
    car_url: str
        the url of each car   
    '''

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all('div', {'class': 'vehicle-card'})

    for item in results:
        model.append(item.find('h2').text)
        mileage.append(item.find('div', {'class': 'mileage'}).text)
        price.append(item.find('span',  {'class': 'primary-price'}).text)
        dealer.append(item.find('strong').text)
        dealer_rating.append(item.find('span',  {'class': 'sds-rating__count'}).text) if item.find('span',  {'class': 'sds-rating__count'}) else dealer_rating.append('-1')
        car_url.append(item.find('a',  {'class': 'vehicle-card-link js-gallery-click-link'})['href']) if item.find('a',  {'class': 'vehicle-card-link js-gallery-click-link'}) else car_url.append('')

    return model, mileage, price, dealer, dealer_rating, car_url


def multi_page_scraping(brands, n):
    '''
    This function is responsible for scraping mutiple pages of the car selling website

    Parameters:
    -------------------------
    brands: list of str
        this is a list that contains car brands I want to scrape
    n: int
        the number of pages I want to scrape for each brand

    Returns
    -------------------------
    listed_cars: pandas dataframe
        this is a dataframe contains attributes for each car
    '''
    print('System is scraping data from websites, please wait...')
    model, mileage, price, dealer, dealer_rating, car_url = [], [], [], [], [], []
    for brand in brands:
        for i in range(1, n+1):
            url = f'https://www.cars.com/shopping/results/?list_price_max=&makes[]={brand}&maximum_distance=all&models[]=&page={i}&stock_type=cpo&zip=48108'
            model, mileage, price, dealer, dealer_rating, car_url = page_scraping(url, model, mileage, price, dealer, dealer_rating, car_url)
            # print(len(model), len(mileage), len(price), len(dealer), len(dealer_rating), len(car_url))
    listed_cars = pd.DataFrame({'model':model, 'mileage':mileage, 'price': price, 'dealer':dealer, 'dealer Rating': dealer_rating, 'url': car_url})

    return listed_cars

def preprocessing_data(data):
    '''
    This function is response for proprocessing scraped data, such as converting data to proper data types, remove commas and so on

    Parameters
    ----------------------
    data: pandas dataframe
        this is a dataframe contains attributes for each car

    Returns
    data: pandas dataframe
        this is a dataframe contains attributes for each car
    '''

    #  seperate year, brand, and model
    col1 = data.loc[:,'model']
    year, brand, model = [], [], []
    for car in col1:
        car = list(car.strip().split())
        year.append(int(car[0]))
        brand.append(car[1])
        model.append(' '.join(car[2:]))
    

    col2 = data.loc[:,'mileage']
    mileage = []
    for p in col2:
        p = list(p.replace(',','').strip().split(' '))
        mileage.append(int(p[0]))

    col3 = data.loc[:,'price']
    price = []
    for m in col3:
        price.append(int(m.replace('$','').replace(',','')))

 
    
    data = data.drop(columns=['model','mileage','price'])
    data = data.assign(year = year, brand = brand, model = model, mileage = mileage, price = price)
    save_or_not = input('Data scraping is finished. Do you want to save the data? Please enter yes or no: ')
    if save_or_not == 'yes':
        file_name = input('Please enter the file name: ')
        data.to_json(file_name)
    return data







def iterate_through_tree(tree, data, questions):
    '''
    This function allows users to iterate tree for as many times as they want. Once all decisions are made, 
    this function prints out matched cars in the form of table. 

    Parameters
    --------------------
    data: pandas dataframe
        a dataframe that contains pandas 
    tree: nested dictionary
        a tree that divides data into each leaf node
    questions: list of str
        a question in the list is responses for one level in the tree

    '''
    
    if not isinstance(tree, list):
        print(questions.pop(0))
        keys = list(tree.keys())
        for idx, k in enumerate(keys):
            print(f'{idx}. {k}')
        answer = int(input(f'Please enter the index for the option: '))
        print()
        iterate_through_tree(tree[keys[answer]],data, questions)
    else:
        if tree:
            print_result(tree, data)
        else:
            print('Sorry, no car matches all requirements in the database')
        print()

def print_result(indices, data):
    '''
    This function prints out the matched cars in a readable format

    Parameters
    -----------------------
    indices: list of int
        this contains indices of matched cars in the dataframe
    data: pandas dataframe
        a dataframe contains information of cars
    '''
    print("{:<10} {:<10} {:<30} {:<15} {:<15} {:<50} {:<10} ".format('Year','Brand','Model', 'Mileage/mi', 'Price/$', 'Dealer', 'Dealer Rating'))

    for idx in indices:
        row_list = data.loc[idx, :].values.flatten().tolist()
        print("{:<10} {:<10} {:<30} {:<15} {:<15} {:<50} {:<10} ".format(row_list[3],
                                                                         row_list[4],
                                                                         row_list[5],
                                                                         row_list[6],
                                                                         row_list[7],
                                                                         row_list[0],
                                                                         row_list[1],
                                                                         ))
def main():
    '''
    This function combines all components of the program. User will be able to iterate through the tree and find matched cars
    '''
    brands = ['cadillac', 'bmw', 'ford', 'porsche', 'toyota', 'volkswagen']
    n = 5
    questions = ['Please pick a car brand you would like to purchase: ',
                 'Please pick the age of the car you would like to purchase: ',
                 'Please pick the price you would like to pay for: ',
                 'Please pick the mileage of the car you would like to purchase: ']
    

    load_or_not = input('Do you want to scrape data or load from the cache? Please enter 1 for scraping data or 2 for loading from the cache: ')
    if load_or_not == '1':
        listed_cars = multi_page_scraping(brands, n)
        processed_data = preprocessing_data(listed_cars)
        
    else:
        data_file = input('Please enter the file name: ')
        while not os.path.isfile(data_file):
            data_file = input('The file you entered doesn\'t exist, please enter the file name again: ')
        processed_data = pd.read_json(data_file)

    if os.path.isfile('tree.json'):
        print('load')
        f = open('tree.json')
        tree = json.load(f)
        f.close()
    else:
        print('build')
        tree = build_tree(processed_data, brands)

    while True:
        query = questions.copy()
        iterate_through_tree(tree, processed_data, query)
        play_again = input('Do you want to change your requirements and search again? Please enter yes or no: ')
        if play_again == 'no':
            break

    print('Bye!')

if __name__ == '__main__':

    main()
    