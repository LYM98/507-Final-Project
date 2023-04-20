import requests
from bs4 import BeautifulSoup
import pandas as pd
import os.path


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
        car_url.append(item.find('a',  {'class': 'vehicle-card-link js-gallery-click-link'})['href']) if item.find('a',  {'class': 'vehicle-card-link js-gallery-click-link'}) else car_url.append('')

    return model, mileage, price, dealer, dealer_rating, car_url


def multi_page_scraping(brands, n):
    print('System is scraping data from websites, please wait...')
    model, mileage, price, dealer, dealer_rating, car_url = [], [], [], [], [], []
    for brand in brands:
        for i in range(1, n+1):
            url = f'https://www.cars.com/shopping/results/?list_price_max=&makes[]={brand}&maximum_distance=all&models[]=&page={i}&stock_type=cpo&zip=48108'
            model, mileage, price, dealer, dealer_rating, car_url = page_scraping(url, model, mileage, price, dealer, dealer_rating, car_url)
            # print(len(model), len(mileage), len(price), len(dealer), len(dealer_rating), len(car_url))
    listed_cars = pd.DataFrame({'model':model, 'mileage':mileage, 'price': price, 'dealer':dealer, 'dealer Rating': dealer_rating, 'url': car_url})
    save_or_not = input('Data scraping is finished. Do you want to want save the data? Please enter yes or no: ')
    if save_or_not == 'yes':
        file_name = input('Please enter the file name: ')
        listed_cars.to_json(file_name)
    return listed_cars

def preprocessing_data(data):

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

    return data

def build_tree(data, brands):

    tree = {}
    tree = split_by_brand(data, brands, tree)
    tree = split_by_year(data, tree)
    tree = split_by_price(data, tree)
    tree = split_by_milleage(data, tree)
    return tree


def split_by_brand(data, brands, tree):
    for b in brands:
        tree[b] = []
    for index, row in data.iterrows():

        tree[row['brand'].lower()].append(index)

    return tree

def split_by_year(data, tree):
    statistic = data.loc[:,'year'].describe()
    q1 = int(statistic['25%'])
    q2 = int(statistic['50%'])
    q3 = int(statistic['75%'])
    # min_max = data['year'].agg(['min', 'max'])

    # split = (min_max['min']+min_max['max'])//2

    for key1 in tree.keys():

        subtree = {
                f'Before year {q1}': [],
                f'between year {q1} and {q2}': [],
                f'between year {q2} and {q3}': [],
                f'After year {q3}': []
            }

        for idx in tree[key1]:
            cur_row = data.iloc[[idx]]

            if cur_row['year'].item() < q1:
                subtree[f'Before year {q1}'].append(idx)
            elif cur_row['year'].item() >= q1 and cur_row['year'].item() < q2:

                subtree[f'between year {q1} and {q2}'].append(idx)
            elif cur_row['year'].item() >= q2 and cur_row['year'].item() < q3:

                subtree[f'between year {q2} and {q3}'].append(idx)
            else:
                subtree[f'After year {q3}'].append(idx)
        
        tree[key1] = subtree


    return tree

def split_by_price(data, tree):

    statistic = data.loc[:,'price'].describe()
    q1 = int(statistic['25%'])
    q2 = int(statistic['50%'])
    q3 = int(statistic['75%'])

    for key1 in tree.keys():
        for key2 in tree[key1].keys():
            subtree = {
                 f'Under ${q1}': [],
                 f'between ${q1} and ${q2}': [],
                 f'between ${q2} and ${q3}': [],
                 f'Higher than ${q3}': []
             }
            
            for idx in tree[key1][key2]:
                cur_row = data.iloc[[idx]]
                if cur_row['price'].item() < q1:

                    subtree[f'Under ${q1}'].append(idx)
                elif cur_row['price'].item() >= q1 and cur_row['price'].item() < q2:

                    subtree[f'between ${q1} and ${q2}'].append(idx)
                elif cur_row['price'].item() >= q2 and cur_row['price'].item() < q3:

                    subtree[f'between ${q2} and ${q3}'].append(idx)
                else:
                    subtree[f'Higher than ${q3}'].append(idx)
            tree[key1][key2] = subtree
            
    return tree

def split_by_milleage(data, tree):
    statistic = data.loc[:,'mileage'].describe()
    q1 = int(statistic['25%'])
    q2 = int(statistic['50%'])
    q3 = int(statistic['75%'])    

    for key1 in tree.keys():
        for key2 in tree[key1].keys():
            for key3 in tree[key1][key2].keys():

                subtree = {
                 f'Under {q1}mi': [],
                 f'between {q1}mi and {q2}mi': [],
                 f'between {q2}mi and {q3}mi': [],
                 f'Higher than {q3}mi': []
                }

                for idx in tree[key1][key2][key3]:
                    cur_row = data.iloc[[idx]]
                    if cur_row['mileage'].item() < q1:

                        subtree[f'Under {q1}mi'].append(idx)
                    elif cur_row['mileage'].item() >= q1 and cur_row['mileage'].item() < q2:

                        subtree[f'between {q1}mi and {q2}mi'].append(idx)
                    elif cur_row['mileage'].item() >= q2 and cur_row['mileage'].item() < q3:

                        subtree[f'between {q2}mi and {q3}mi'].append(idx)
                    else:
                        subtree[f'Higher than {q3}mi'].append(idx)

                tree[key1][key2][key3] = subtree

    return tree





def iterate_through_tree(tree, data, questions):
    
    
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

    brands = ['cadillac', 'bmw', 'ford', 'porsche', 'toyota', 'volkswagen']
    n = 5
    questions = ['Please pick a car brand you would like to purchase: ',
                 'Please pick the age of the car you would like to purchase: ',
                 'Please pick the price you would like to pay for: ',
                 'Please pick the mileage of the car you would like to purchase: ']
    

    load_or_not = input('Do you want to scrape data or load from the cache? Please enter 1 for scraping data or 2 for loading from the cache: ')
    if load_or_not == '1':
        listed_cars = multi_page_scraping(brands, n)
    else:
        data_file = input('Please enter the file name: ')
        while not os.path.isfile(data_file):
            data_file = input('The file you entered doesn\'t exist, please enter the file name again: ')
        listed_cars = pd.read_json(data_file)

    processed_data = preprocessing_data(listed_cars)
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
    