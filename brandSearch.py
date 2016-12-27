#! /bin/python
from pyspark import SparkContext, SparkConf
import json
from pprint import pprint

#config path
brands_path = "brands.txt"
metadata_path = "hdfs:///datasets/amazon-reviews/metadata.json"
#metadata_path = "file:///home/staes/shuffled_metadata.json"


# load the list of brands
brands = []
with open(brands_path) as f:
	for line in f:
		line = line.rstrip('\n').lower()
		brands.append(line)

# lookup if a certain brand is swiss
def searchBrand(line):
	line = line.rstrip('\n').lower()
	d = eval(line)
	if 'brand' in d:
		if d['brand'] in brands:
			return ("Swiss brand", [d])
		else:
			return ("No Swiss brand", 1)
	else:
		return ("No brand", 1)

# load spark job
conf = SparkConf().setAppName("SoA").setMaster("local")
sc = SparkContext(conf=conf)

# load metadata file
text_file = sc.textFile(metadata_path)

# map reduce -> 
# for each product lookup if it is swiss, keeps brand:productkey (map)
# group products of the same brand, keeps brand:[productkeys] (reduce)
counts = text_file \
             .map(searchBrand) \
             .reduceByKey(lambda a, b: a + b)
products = counts.collect()
print(products)

# create json file containing only swiss products
f = open('swiss_products.json','w')
products = dict(products)
for product in products['Swiss brand']:
	f.write(str(product) + '\n')
f.close()