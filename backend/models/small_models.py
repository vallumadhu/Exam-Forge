from transformers import AutoTokenizer, AutoModelForCausalLM

class Model:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.tokenizer = None
        self.model = None

    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id)

    def invoke(self, text: str, max_new_tokens: int = 512) -> str:
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


model = Model("microsoft/Phi-3-mini-4k-instruct")
model.load()