from bson.code import Code

sentiment_avg = [{
    "$group": {
        "_id": "null",
        "sentiment_avg": {
            "$avg": "$chirp.sentiment.polarity"
        }
    }
}]

sentiment_count_mr = {
    'mapper': Code('''
        function() {
            var polarity = this.chirp.sentiment.polarity;

            if (polarity > 0) {
                emit('positive', 1);
            } else if (polarity < 0)  {
                emit('negative', 1);
            } else {
                emit('neutral', 1);
            }
        }
    '''),
    'reducer': Code('''
        function(key, values) {
            return Array.sum(values);
        }
    ''')
}

sentiment_country_mr = {
    'mapper': Code('''
        function() {
            emit(this.place.country_code, this.chirp.sentiment.polarity);
        }
    '''),
    'reducer': Code('''
        function(key, values) {
            return Array.avg(values);
        }
    '''),
    'query': {"place.country_code": {"$exists": True}}
}

sentiment_date_mr = {
    'mapper': Code('''
        function() {
            var date = new Date(this.created_at);
            var label = 'neutral';
            var polarity = this.chirp.sentiment.polarity;

            if (polarity > 0) {
                label = 'positive';
            } else if (polarity < 0)  {
                label = 'negative';
            }

            emit({'year': date.getFullYear(),
                'month': date.getMonth(),
                'day': date.getDate(),
                'sentiment': label}, 1);
        }
    '''),
    'reducer': Code('''
        function(key, values) {
            return Array.sum(values);
        }
    '''),
    'query': {'$and': [
        {'chirp.sentiment': {'$exists': True}},
        {'created_at': {'$exists': True}}
    ]}
}

tweets_total_country_mr = {
    'mapper': Code('''
        function() {
            emit(this.place.country_code, 1);
        }
    '''),
    'reducer': Code('''
        function(key, values) {
            return Array.sum(values);
        }
    '''),
    'query': {'place.country_code': {'$exists': True}}
}
