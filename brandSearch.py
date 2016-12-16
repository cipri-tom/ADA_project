#! /bin/python
from pyspark import SparkContext, SparkConf

def searchBrand(line):
	if("Rolex" in line):
		return ("Rolex", 1) 
	else:
		return ("No Brand", 1)

conf = SparkConf().setAppName("SoA").setMaster("local")
sc = SparkContext(conf=conf)

metadata_path = "hdfs:///datasets/amazon-reviews/metadata.json"
#metadata_path = "file:///home/staes/shuffled_metadata.json"
text_file = sc.textFile(metadata_path)
print('ok')

counts = text_file \
             .map(searchBrand) \
             .reduceByKey(lambda a, b: a + b)
print(counts.collect())
#.flatMap(lambda line: line.split(" ")) \
#counts.saveAsTextFile("file:///home/staes/test.txt")