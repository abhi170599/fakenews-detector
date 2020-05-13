import tensorflow as tf 
import json
import numpy as np 

from flask import Flask,request,jsonify
from flask_cors import CORS 

from keras.models import load_model
from gensim.models.doc2vec import Doc2Vec

from Util.utils import DataExtractor

graph = tf.get_default_graph()

app = Flask(__name__)
CORS(app)

""" initialize data extractor """
CONSUMER_KEY = "U4PIXA8sDWKVU4Z92Gq5vnZ3K"
CONSUMER_SEC = "FPx5WjnEJP6DhfdlUMcfSjm8qRM6gxZ59ByVCuLAiyDbEtffuR"

ACCESS_TOKEN = "1030553232991346688-HPhQwKivBvJL2ctA2Afd6uIzRPAtzx"
ACCESS_SECRT = "oejEX448ymzSiKDNccpzi7eWBZ9dlCRiUXJeMYAlDDphG"


cred_dict = {
             "CONSUMER_KEY":CONSUMER_KEY,
             "CONSUMER_SEC":CONSUMER_SEC,
             "ACCESS_TOKEN":ACCESS_TOKEN,
             "ACCESS_SECRT":ACCESS_SECRT  
            }

config = [cred_dict]






model = load_model('Util/rumour-detector_v2.h5')
d2v   = Doc2Vec.load('Util/d2v_v2.model')

extractor = DataExtractor(config,d2v,1,num_hours=50)

@app.route("/validate",methods=['GET'])
def validate():

    query = request.args.get('q')

    vec   = extractor.get_vectors_for_query(query)
    
    res = ""
    if vec is None:
        res = "rephrase"
    else:
        with graph.as_default():
            pred = model.predict(np.reshape(vec,(1,50,50)))
        print(pred) 
        idx = np.argmax(pred[0])
        if idx==0:
            res="fake"
        else:
            res="verified"

    response = {
        "res":res
    }

    return jsonify(response)        


if __name__=="__main__":
    app.run(host='0.0.0.0') 

