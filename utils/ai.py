from utils.tokenizer import tokenize
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import os

# assert tf.__version__.startswith('2')
# tf.get_logger().setLevel('ERROR')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

def remove_symbols(tokens: list):
    return [w for w in tokens if w.isalpha()]


en_stop_words = set(stopwords.words('english'))


def remove_stop_words(tokens: list):
    filtered = [w for w in tokens if w not in en_stop_words]
    return filtered


lemmatizer = WordNetLemmatizer()


def lemmatizer_proc(tokens: list, lemmatizer: WordNetLemmatizer):
    filtered = [lemmatizer.lemmatize(w) for w in tokens]
    return filtered


stemmer = PorterStemmer()


def stemming_proc(tokens: list, stemmer: PorterStemmer):
    filtered = [stemmer.stem(w) for w in tokens]
    return filtered


def process_text(raw_text):
    raw_tokens = word_tokenize(raw_text)
    clean_tokens = remove_symbols(raw_tokens)
    clean_tokens = remove_stop_words(clean_tokens)
    lemm_tokens = lemmatizer_proc(clean_tokens, lemmatizer)
    stemm_tokens = stemming_proc(lemm_tokens, stemmer)

    processed_text = " ".join(stemm_tokens)

    print(f"original[{len(raw_tokens)}]:", raw_text)
    print(f"processed[{len(processed_text)}]:", processed_text)

    return processed_text


# Convert the model
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'is_toxic_model/saved_model')
converter = tf.lite.TFLiteConverter.from_saved_model(filename)
tflite_model = converter.convert()

interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()

output = interpreter.get_output_details()[0]  # Model has single output.
input = interpreter.get_input_details()[0]  # Model has single input.


def predict(raw_test_message):
    processed_test_message = process_text(raw_test_message)
    vect_data = tokenize(processed_test_message)
    input_data = tf.constant(vect_data, shape=[1, 20])
    interpreter.set_tensor(input['index'], input_data)
    interpreter.invoke()
    res = interpreter.get_tensor(output['index'])
    return res
