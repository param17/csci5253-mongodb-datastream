import os


class Constants:
    class EnvConfig:
        gnip_api_username = os.environ['TWITTER_UNAME']
        gnip_api_password = os.environ['TWITTER_PASS']
        gnip_api_auth_url = os.environ['TWITTER_URL']
        kafka_server = [str(os.environ['KAFKA_IP']) + ":" + os.environ["KAFKA_PORT"]]
        retries = [os.environ['RETRIES']]

    class JSONKeys:
        requiredKeys = ['text', 'place']
        optional_location = 'location'
        search_string = 'searchString'
        total_tweets = 'totalTweets'
        exception = 'exception'

    class Topics:
        receiving = 'search_string'
        sending = 'tweets'
        consumer_group_name = 'TwitterSearchString'

    class GNIP:
        language = 'en'
        filter_param = 'geo'
        # TODO: Discuss later!
        hard_max = 2000
