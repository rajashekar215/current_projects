import redis
#from langdetect import detect
redisClient = redis.Redis(host='localhost', port=6379)
languages = {1:"te",2:"ta",3:"hi",4:"kn",5:"ml",6:"mr",7:"bn",8:"gu",9:"pa",11:"en"}
def getVectors(sentence, langCode):
    if sentence == None or sentence == '':
        #print(None)
        return [None]
    else:
        language = languages[langCode]
        #print(language)
        words = sentence.split(' ')
        returnData = []
        for word in words:
                vectors = redisClient.get(language + ":" + word)
                returnData.append(vectors)
        # if language == "te":
        #     for word in words:
        #         vectors = redisClient.get(word)
        #         returnData.append(vectors)
        # else:
        #     for word in words:
        #         vectors = redisClient.get(language + word)
        #         returnData.append(vectors)
        #print(returnData)
        return returnData
#getVectors('రెండు')
