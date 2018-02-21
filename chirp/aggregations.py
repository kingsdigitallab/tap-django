sentiment_avg = [{
    '$group': {
        '_id': 'null',
        'sentiment_avg': {
            '$avg': '$chirp.sentiment.polarity'
        }
    }
}]
