#### Tweets Producer
This module is responsible for making the gnip api calls to twitter's Enterprise API. This module consumes what has been input into the kafka topic "search_string" and this query string is used as query string to the api. The recieved tweets are then input to the kafka queue "tweets".


### Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

#### Dependencies to be installed

```
Kafka
Mongo Connector
```