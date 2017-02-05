#! /bin/python
from pyspark import SparkContext, SparkConf
import json
from pprint import pprint
import pickle
import re


#config path
brands_path = "../data/wiki_brands.txt"
brands_path2 = "../data/all_swiss_brands.pickle"
metadata_path = "hdfs:///datasets/amazon-reviews/metadata.json"


# load the list of brands
brands = []
with open(brands_path) as f:
	for line in f:
		line = line.rstrip('\n').lower()
		brands.append(line)

with open(brands_path2, 'rb') as fp:
    new_brands = pickle.load(fp)

# clean brand data
for b in new_brands:
	b = b.lower()
	b = re.sub(" [\(\[].*?[\)\]]", "", b)
	brands.append(b)

brands = list(set(brands))

# lookup if a certain brand is swiss
def searchBrand(line):
	line = line.rstrip('\n').lower()
	d = eval(line)
	if 'brand' in d:
		if d['brand'] in brands:
			return ("Swiss brand", [d])
			#return (d['brand'], d['asin'])
		else:
			return ("No Swiss brand", 1)
	else:
		return ("No brand", 1)

# load spark job
conf = SparkConf().setAppName("SoA")
sc = SparkContext(conf=conf)

# load metadata file
text_file = sc.textFile(metadata_path)

print("finished loading file and brands")

# map reduce -> 
# for each product lookup if it is swiss, keeps brand:productkey (map)
# group products of the same brand, keeps brand:[productkeys] (reduce)
counts = text_file \
             .map(searchBrand) \
             .reduceByKey(lambda a, b: a + b)
products = counts.collect()

print("finished map reduce")
#print(products)

# create json file containing only swiss products
f = open('../data/swiss_products.json','w')
products = dict(products)
for product in products['Swiss brand']:
	f.write(str(product) + '\n')
f.close()

print("finished writing file")