# SOA -- Swiss on Amazon

## Abstract
We will work with the Amazon review dataset, which contains a list of 9.7 million products. We will do a mapping based on the product’s brand to find out which products are Swiss. Once this mapping is done we will study the prices of Swiss products and the reviews of these products. We will try to answer the following questions:
How expensive are Swiss products compared to the world?
Is there a relation between the price of a product and its rating?
How do people feel towards Swiss products?


Additional ideas:
 - How the review of a product evolved in time?
 - Which canton in Switzerland has the most expensive products on Amazon?


## Data description
We will work with a dataset of Amazon that contains product reviews and metadata from Amazon, including 142.8 million reviews spanning May 1996 - July 2014. A description of this data can be found at http://jmcauley.ucsd.edu/data/amazon/. For this project we will work with the entire review data set sorted by product. This dataset is 18gb large. Additionally we will work with the metadata, which contains information about the products, which is 3.1gb large. Considering the size of this data we can say that one challenging aspect of our project will be to handle big data. 

## Feasibility and Risks
The first part of the project focuses on mapping Amazon products to Switzerland. To do this, we’ll need a list of Swiss brands, which may prove difficult to find or build. We believe open data exists regarding companies registered in CH, but not a comprehensive list of their brands. We propose a few methods to get from companies to brands, from using Wikipedia or Wikidata to scraping companies’  websites, so it is feasible we will get a decent database to work with.
Another unknown for this part concerns the actual number of Swiss products in the dataset. Although the dataset is big, it was acquired by crawling the US version of Amazon, so there is a risk that the number of products from Switzerland is relatively small. If this is the case, we will need to propose some different strategies and analyses to be performed.


Regarding the technical side of the project, we consider the size of the dataset to pose some problems. We will have to use Spark in working with the data, which is new to all members of the team. However, if the encountered problems turn into real obstacles, the dataset offers smaller cores which would fit in memory. 

## Deliverables
At the moment, the main deliverable we have in mind is a system that is robust and efficient enough to identify Swiss products in the Amazon dataset. We want it to be extensive enough to identify most brands, not only the ones from well known companies.
After this mapping process we can identify relations and correlations (using statistical tests) between product categories and prices when compared to the rest of the world and among different cantons.

A second, more involved analysis, consists in using the products’ ratings and reviews to identify how the customers *feel* about specific Swiss products. In order to perform sentiment analysis (or opinion mapping) on the Amazon reviews we will most likely follow similar projects or research papers as the one [here](https://journalofbigdata.springeropen.com/articles/10.1186/s40537-015-0015-2) (additional useful resources were found [here](https://courses.cs.sfu.ca/2015fa-cmpt-733-g1/pages/Assignment3/view) as well). Moreover the timestamps of the reviews can be used to create a timeline of how the opinions of the customers evolved.

For visualizing the results we plan on using a cantonal map similar to the one we used in the third assignment, only that this time we will be using Swiss products’ prices, ratings, or customer opinions. We will also use a word cloud visualization of the adjectives used to describe certain products.

## Timeplan
 - **Now - 1.12**: gather/map product data
 - **1.12 - 15.12**: swiss products data analysis (in parallel start on opinion mining)
 - **15.12**: checkpoint 
 - **15.12 - 23.12**: sentiment analysis on the product reviews
 - **1.01-15.01.2017**: answer questions about data and implement the visualizations
 - **End january**: presentation






