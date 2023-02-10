f = open('utils/is_toxic_model/vocab', "r")
text = f.readlines()
tokens = {}
for t in text:
    texts = t.split()
    tokens[texts[0]] = int(texts[1][:])


def tokenize(text, maxlen=22):
    res = [0] * 22
    res[0] = 1
    splitted = text.split()
    for i in range(0, maxlen - 1):
        if i >= len(splitted):
            break
        if splitted[i] in tokens:
            res[i+1] = tokens[splitted[i]]

    return res
