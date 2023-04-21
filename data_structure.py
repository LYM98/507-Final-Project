import json
import os
def load_tree(processed_data, brands):
    '''
    This function is responsible for creating or loading the tree.
    If tree file exists, then load the tree, else create the tree
    '''
    if os.path.isfile('tree.json'):
        f = open('tree.json')
        tree = json.load(f)
        f.close()
    else:
        tree = build_tree(processed_data, brands)

    return  tree


def build_tree(data, brands):
    '''
    This function responsible for building the tree with scraped data
    
    Parameters
    --------------------
    data: pandas dataframe
        a dataframe that contains pandas 
    brands: list of str
        a list contains brands 

    Returns
    --------------------
    tree: nested dictionary
        a tree that divides data into each leaf node
    '''
    tree = {}
    tree = split_by_brand(data, brands, tree)
    tree = split_by_year(data, tree)
    tree = split_by_price(data, tree)
    tree = split_by_milleage(data, tree)

    with open("tree.json", "w") as fp:
        json.dump(tree,fp)     
    return tree


def split_by_brand(data, brands, tree):
    '''
    This function responsible for building the tree with scraped data.
    More specifically, grow leaf nodes based on the brand of used cars

    Parameters
    --------------------
    data: pandas dataframe
        a dataframe that contains pandas 
    brands: list of str
        a list contains brands 
    tree: nested dictionary
        a tree that divides data into each leaf node

    Returns
    --------------------
    tree: nested dictionary
        a tree that divides data into each leaf node
    '''
    for b in brands:
        tree[b] = []
    for index, row in data.iterrows():

        tree[row['brand'].lower()].append(index)

    return tree

def split_by_year(data, tree):
    '''
    This function responsible for building the tree with scraped data.
    More specifically, grow leaf nodes based on the age of used cars
    
    Parameters
    --------------------
    data: pandas dataframe
        a dataframe that contains pandas 
    tree: nested dictionary
        a tree that divides data into each leaf node

    Returns
    --------------------
    tree: nested dictionary
        a tree that divides data into each leaf node
    '''
    statistic = data.loc[:,'year'].describe()

    split= int(statistic['50%'])
 
    # min_max = data['year'].agg(['min', 'max'])

    # split = (min_max['min']+min_max['max'])//2

    for key1 in tree.keys():

        subtree = {
                f'Before year {split}': [],
                f'After year {split}': []
            }

        for idx in tree[key1]:
            cur_row = data.iloc[[idx]]

            if cur_row['year'].item() < split:
                subtree[f'Before year {split}'].append(idx)
            else:
                subtree[f'After year {split}'].append(idx)
        
        tree[key1] = subtree


    return tree

def split_by_price(data, tree):
    '''
    This function responsible for building the tree with scraped data.
    More specifically, grow leaf nodes based on the price of used cars
    
    Parameters
    --------------------
    data: pandas dataframe
        a dataframe that contains pandas 
    tree: nested dictionary
        a tree that divides data into each leaf node

    Returns
    --------------------
    tree: nested dictionary
        a tree that divides data into each leaf node
    '''
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
    '''
    This function responsible for building the tree with scraped data.
    More specifically, grow leaf nodes based on the mileage of used cars
    
    Parameters
    --------------------
    data: pandas dataframe
        a dataframe that contains pandas 
    tree: nested dictionary
        a tree that divides data into each leaf node

    Returns
    --------------------
    tree: nested dictionary
        a tree that divides data into each leaf node
    '''
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