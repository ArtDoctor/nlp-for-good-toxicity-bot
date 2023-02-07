from googletrans import Translator
import pandas as pd

translator = Translator()
dt1 = translator.detect('hello')
print(dt1)

df = pd.read_csv('toxicity_en.csv')

print(df.iloc[1])
