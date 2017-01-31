import csv
import os
import pickle

product_file = 'max/productcategories.pickle'
path = 'max/'
filename = 'amazon_ratings.csv'
files = os.listdir('max')
if filename in files:
    files.remove(filename)

with open (product_file, 'rb') as fp:
    categories = pickle.load(fp)

with open(path + filename, 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'item_id', 'rating', 'timestamp', 'category'])

    for ratings_file in files:
        extracted_name = ratings_file[8:(len(ratings_file)-4)] \
                            .replace("_", " ")
        with open(path + ratings_file, 'rb') as f2:
            for entry in f2:
                if entry != "":
                    data = eval(entry)
                    writer.writerow([data['reviewerID'], data['asin'],
                                    data['overall'], data['unixReviewTime'], categories[data['asin'].lower()]])

