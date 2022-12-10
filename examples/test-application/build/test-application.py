from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.types import *

conf = SparkConf()

conf.set("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
conf.set("spark.hadoop.fs.s3a.access.key", "silveira")
conf.set("spark.hadoop.fs.s3a.secret.key", "guilherme@123")
conf.set("spark.hadoop.fs.s3a.path.style.access", True)
conf.set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
conf.set('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')
conf.set("hive.metastore.uris", "thrift://metastore:9083")
conf.setAppName("test-application")

spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

data2 = [("James","","Smith","36636","M",3000),
    ("Michael","Rose","","40288","M",4000),
    ("Robert","","Williams","42114","M",4000),
    ("Maria","Anne","Jones","39192","F",4000),
    ("Jen","Mary","Brown","","F",-1)
  ]

schema = StructType([ \
    StructField("firstname",StringType(),True), \
    StructField("middlename",StringType(),True), \
    StructField("lastname",StringType(),True), \
    StructField("id", StringType(), True), \
    StructField("gender", StringType(), True), \
    StructField("salary", IntegerType(), True) \
  ])
 
df = spark.createDataFrame(data=data2,schema=schema)

df.write.format('parquet').save('s3a://raw/test/')
  