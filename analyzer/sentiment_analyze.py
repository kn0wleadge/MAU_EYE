
import torch
from transformers import AutoModelForSequenceClassification
from transformers import BertTokenizerFast
import logging
tokenizer = BertTokenizerFast.from_pretrained('blanchefort/rubert-base-cased-sentiment-rusentiment')
model = AutoModelForSequenceClassification.from_pretrained('blanchefort/rubert-base-cased-sentiment-rusentiment', return_dict=True)

@torch.no_grad()
def predict(text:str):

    inputs = tokenizer(text, max_length=512, padding=True, truncation=True, return_tensors='pt')
    outputs = model(**inputs)
    predicted = torch.nn.functional.softmax(outputs.logits, dim=1)
    predicted = torch.argmax(predicted, dim=1).numpy()
    result = {"value" : predicted, "assesment" : None}
    if predicted == 0:
        result["assesment" ]= "neutral"
    elif predicted == 1:
        result["assesment"] = "positive"
    else:
        result['assesment'] = "negative"
    return result

if __name__ == "__main__":
    text = "Мой университет - очень плохое место)"
    try:
        print(predict(text))
    except Exception as e:
        print(e)