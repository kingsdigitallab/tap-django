sentiment_avg = [{
    '$group': {
        '_id': 'null',
        'sentiment_avg': {
            '$avg': '$chirp.sentiment.polarity'
        }
    }
}]

words_top_200 = [
    {
        "$unwind": "$chirp.words"
    },
    {
        "$project": {
            "word": {
                "$toLower": "$chirp.words"
            }
        }
    },
    {
        "$group": {
            "_id": "$word",
            "value": {
                "$sum": 1
            }
        }
    },
    {
        "$sort": {
            "value": -1
        }
    },
    {
        "$limit": 200
    }
]
