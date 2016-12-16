#! /bin/python
from pyspark import SparkContext, SparkConf


conf = SparkConf().setAppName("SoA").setMaster("local")
sc = SparkContext(conf=conf)

metadata_path = "hdfs:///datasets/amazon-reviews/metadata.json"
text_file = sc.textFile(metadata_path)
print('ok')

counts = text_file \
             .map(lambda word: ("a", 1)) \
             .reduceByKey(lambda a, b: a + b)
print(counts.collect())
#.flatMap(lambda line: line.split(" ")) \
#counts.saveAsTextFile("test.txt")

'''
counts = text_file.flatMap(lambda line: line.split(" ")) \
             .map(lambda word: (word, 1)) \
             .reduceByKey(lambda a, b: a + b)
counts.saveAsTextFile("/home/staes/test.txt")
'''