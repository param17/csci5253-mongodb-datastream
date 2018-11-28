import json

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from constants import Constants
from multiprocessing import Process
from pymongo import MongoClient
import re


def json_deserializer(received_message):
    try:
        return json.loads(received_message.decode('utf-8', 'ignore'))
    except ValueError:
        return json.dumps({Constants.JSONKeys.exception: True})


def query_mongo_db(mongo_client, received_search_string_json, process_lambda_after_every_batch_fetch):
    search_string = received_search_string_json[Constants.JSONKeys.search_string]
    db = mongo_client[Constants.MongoDB.Config.db_name]
    product_reviews = db[Constants.MongoDB.Config.collection_name]
    regex = re.compile(".*{}.*".format(search_string), re.IGNORECASE)
    reviews_related_to_search = product_reviews.find({Constants.MongoDB.Keys.review, regex})
    process_lambda_after_every_batch_fetch(reviews_related_to_search)


def send_data_to_kafka_in_parallel(tweets, list_of_running_processes):
    process = Process(target=send_tweets_to_kafka, args=(tweets,))
    list_of_running_processes.append(process)
    process.start()


def send_tweets_to_kafka(tweets):
    tweets = list(tweets)
    total_tweets = len(tweets)
    futures = []
    # Need to create a new Producer in every process otherwise messages are not sent to Kafka!
    tweet_producer = KafkaProducer(bootstrap_servers=Constants.EnvConfig.kafka_server,
                                   retries=Constants.EnvConfig.retries)

    for x in tweets:
        # print(x['text'])
        filtered_tweet = {k: v for (k, v) in x.items() if k in Constants.JSONKeys.requiredKeys}

        filtered_tweet[Constants.JSONKeys.search_string] = received_json[Constants.JSONKeys.search_string]
        filtered_tweet[Constants.JSONKeys.total_tweets] = Constants.GNIP.hard_max
        tweet_json_str = json.dumps(filtered_tweet)
        future = tweet_producer.send(Constants.Topics.sending, tweet_json_str.encode('ascii', 'ignore'))
        futures.append(future)
    print("Python Module: Sending %d Tweets to Spark Module" % total_tweets)

    for i, future in enumerate(futures):
        try:
            _ = future.get(timeout=10)
        except KafkaError as e:
            print('Tweet number %i was not sent to Kafka. Reason: %s' % i, str(e))
            pass


if __name__ == "__main__":
    search_string_consumer = KafkaConsumer(Constants.Topics.receiving, group_id=Constants.Topics.consumer_group_name,
                                           bootstrap_servers=Constants.EnvConfig.kafka_server,
                                           value_deserializer=json_deserializer)

    for message in search_string_consumer:
        received_json = message.value
        if Constants.JSONKeys.exception in received_json:
            print('Invalid message received')
            continue

        print('Received string: ' + str(received_json))

        processes = []
        client = MongoClient(Constants.MongoDB.Config.server, Constants.MongoDB.Config.port)
        query_mongo_db(client, received_json, lambda tweets: send_data_to_kafka_in_parallel(tweets, processes))
        print("Number of running processes: %d" % len(processes))
        for proc in processes:
            proc.join()
