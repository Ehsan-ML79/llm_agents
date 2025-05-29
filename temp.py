import openai

openai.api_key = "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"  # Same one you use in LangChain

models = openai.models.list()
for model in models.data:
    print(model.id)