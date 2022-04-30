                 # Data Preparation
#Import monotonically_increasing_id and show R
from pyspark.sql.functions import monotonically_increasing_id
R.show()

# Use the to_long() function to convert the dataframe to the "long" format.
ratings = to_long(R)
ratings.show()

# Get unique users and repartition to 1 partition
users = ratings.select("User").distinct().coalesce(1)

# Create a new column of unique integers called "userId" in the users dataframe.
users = users.withColumn("userId", monotonically_increasing_id()).persist()
users.show()

# Extract the distinct movie id's
movies = ratings.select("Movie").distinct() 

# Repartition the data to have only one partition.
movies = movies.coalesce(1) 

# Create a new column of movieId integers. 
movies = movies.withColumn("movieId", monotonically_increasing_id()).persist() 

# Join the ratings, users and movies dataframes
movie_ratings = ratings.join(users, "User", "left").join(movies, "Movie", "left")
movie_ratings.show()

##In this point I have distinct userId's and movieId's that are integer data types.

# Split the ratings dataframe into training and test data
(training_data, test_data) = ratings.randomSplit([0.8, 0.2], seed=42)

# Set the ALS hyperparameters
from pyspark.ml.recommendation import ALS
als = ALS(userCol="userId", itemCol="movieId", ratingCol="rating", rank = 10, maxIter = 15, regParam = .1,
          coldStartStrategy="drop", nonnegative = True, implicitPrefs = False)

# Fit the mdoel to the training_data
model = als.fit(training_data)

# Generate predictions on the test_data
test_predictions = model.transform(test_data)
test_predictions.show()

# Import RegressionEvaluator
from pyspark.ml.evaluation import RegressionEvaluator

# Complete the evaluator code
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")

# Extract the 3 parameters
print(evaluator.getMetricName())
print(evaluator.getLabelCol())
print(evaluator.getPredictionCol())

# Evaluate the "predictions" dataframe
RMSE = evaluator.evaluate(test_predictions)

# Print the RMSE
print (RMSE)
