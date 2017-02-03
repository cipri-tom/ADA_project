from pyspark import SparkContext, SparkConf
import json
from pprint import pprint
import pickle
import re
#import yaml

# Open the file containing the asins of the products for 
# which you want the average rating score.
# The idea behind this is to see how much does a specific
# review's rating deviates from the mean rating score of a product

# In this case the file contains the asins of swiss products 
# which received at least 5 helpful flags (or votes)
with open('../data/helpful_asins_bigger.pickle', 'rb') as fp:
    asins = pickle.load(fp)

# The path to the amazon reviews
complete_path = "hdfs:///datasets/amazon-reviews/complete.json"


# load spark job
conf = SparkConf().setAppName("SoA")
sc = SparkContext(conf=conf)

# load file
text_file = sc.textFile(complete_path)

print("Finished loading swiss reviews")

# Transformation pipeline
# Step 1:
# Keep only the product reviews which match the loaded list of asins
def filter_asins(line):
	l = line.strip('\n')
	l = eval(l)
	if(l['asin'] in asins):
		return True
	else:
		return False

# Step 2:
# From the above filtering keep only the 'asin' and 'overall' fields
# from the reviews (the 'overall' field will be kept as part of a list)
def reduce_swiss_review(line):
	l = line.rstrip('\n')
	l = eval(l)
	return (l['asin'], [l['overall']])

# Step 3:
# In the next step use reduceByKey (i.e. on 'asins') to collect
# all the ratings for the respective asin

# Step 4:
# As the ratings are collected as a list compute the average
# of that list and save the result as a dictionary {'asin':'mean rating'}
def mean_score(pair):
	av_score = sum(pair[1])*1.0/len(pair[1])
	temp = {pair[0]:av_score}
	return temp

res = text_file.filter(filter_asins)\
	.map(reduce_swiss_review)\
	.reduceByKey(lambda a, b: a+b)\
	.map(mean_score)

reduced_data = res.collect()

# After collecting the data (quite small in the end) save 
# the resulting dictionaries in a file for later use
write_file = open("../data/asin_ratings_bigger.json","w")
for item in reduced_data:
        write_file.write(str(item)+'\n')


