from transformers import PegasusTokenizer, PegasusForConditionalGeneration, TFPegasusForConditionalGeneration

# Let's load the model and the tokenizer 
model_name = "human-centered-summarization/financial-summarization-pegasus"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name) # If you want to use the Tensorflow model 
                                                                    # just replace with TFPegasusForConditionalGeneration


# Some text to summarize here
text_to_summarize = """
As an essential business throughout the COVID-19 pandemic, we have remained open with our top priority being the health and safety of our employees, customers and community. At this time, the COVID-19 pandemic has not significantly impacted our manufacturing facilities or third parties to whom we outsource certain manufacturing processes, the distribution centers where our inventory is managed or the operations of our logistics and other service providers. We continue working with our customers and suppliers to understand the existing and potential future negative impacts to our delivery and supply chain and take actions in an effort to mitigate such impacts. We continue to actively monitor the pandemic and we will continue to take appropriate steps to mitigate the adverse impacts on our business posed by the on-going spread of COVID-19. The company believes that the fair value assigned to the assets acquired and liabilities assumed are based on reasonable assumptions and estimates that marketplace participants would use.
"""
# Tokenize our text
# If you want to run the code in Tensorflow, please remember to return the particular tensors as simply as using return_tensors = 'tf'
input_ids = tokenizer(text_to_summarize, return_tensors="pt").input_ids

# Generate the output (Here, we use beam search but you can also use any other strategy you like)
output = model.generate(
    input_ids, 
    max_length=1000, 
    num_beams=5, 
    early_stopping=True
)

# Finally, we can print the generated summary
print(tokenizer.decode(output[0], skip_special_tokens=True))