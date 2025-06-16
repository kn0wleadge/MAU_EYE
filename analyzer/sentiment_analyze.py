import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('seara/rubert-tiny2-russian-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('seara/rubert-tiny2-russian-sentiment', return_dict=True)

@torch.no_grad()
def predict(text: str):
    inputs = tokenizer(text, max_length=512, padding=True, truncation=True, return_tensors='pt')
    outputs = model(**inputs)
    predicted_probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    predicted = torch.argmax(predicted_probs, dim=1).numpy()
    
    result = {"value": predicted, "assesment": None}
    if predicted == 0:
        result["assesment"] = "negative"
    elif predicted == 1:
        result["assesment"] = "neutral"
    elif predicted == 2:
        result["assesment"] = "positive"
    else:
        result["assesment"] = "unknown"
    
    return result

if __name__ == "__main__":
    text = "Мой университет - очень плохое место)"
    try:
        print(predict(text))
    except Exception as e:
        print(e)