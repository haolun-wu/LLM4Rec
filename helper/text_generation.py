from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForCausalLM
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers import LlamaTokenizer, LlamaForCausalLM
from transformers import pipeline
import torch
import re
import openai

access_token = "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"


def generate_text(prompt, model_name, device):
    model_dir = '/home/haolun/projects/ctb-lcharlin/haolun/saved_LLM'
    if device == 'cpu':
        device_map = 'cpu'
    else:
        device_map = {i: 0 for i in range(24)}  # For a model with 24 layers, all on GPU 0



    if 't5' in model_name:
        tokenizer = AutoTokenizer.from_pretrained("google/{}".format(model_name), cache_dir=model_dir)
        model = AutoModelForSeq2SeqLM.from_pretrained("google/{}".format(model_name), cache_dir=model_dir).to(device)
    elif model_name == 'gpt2':
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        model = GPT2LMHeadModel.from_pretrained('gpt2').to(device)
    elif model_name == "falcon-7b-instruct":
        tokenizer = AutoTokenizer.from_pretrained("tiiuae/{}".format(model_name),
                                                  cache_dir=model_dir,
                                                  trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained("tiiuae/{}".format(model_name),
                                                     cache_dir=model_dir,
                                                     trust_remote_code=True).to(device)
    elif model_name == 'llama2':
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf",
                                                  cache_dir=model_dir,
                                                  trust_remote_code=True, use_auth_token=access_token)
        model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf",
                                                     cache_dir=model_dir,
                                                     trust_remote_code=True, use_auth_token=access_token).to(device)

    input_string = prompt
    input_string = re.sub(' +', ' ', input_string)

    # Encode the input string
    input_ids = tokenizer.encode(input_string, return_tensors='pt', truncation=True, max_length=1024).to(device)
    print("input_ids:", len(input_ids[0]))
    print(f"Max token ID in input: {input_ids.max()}")


    # Adjust max_length based on your input length
    max_length = len(input_ids[0]) + 50  # Adjust 50 as per your requirement for the output length

    # Make sure max_length does not exceed model's maximum limit
    if max_length > 1024:
        max_length = 1024

    if model_name not in ['gpt2', 'llama-3b', 'llama-7b', 'falcon-7b-instruct', 'llama2']:
        max_length = 200

    if model_name in ['falcon-7b-instruct', 'llama2']:
        max_length = 2048

    print("max_length:", max_length)

    outputs = model.generate(input_ids,
                             pad_token_id=tokenizer.pad_token_id,
                             do_sample=True,  # Set to True to implement top-p sampling
                             max_length=max_length,
                             top_p=0.85,  # Adjust as needed
                             temperature=0.8,
                             num_return_sequences=1)

    # Decode only the new tokens that were generated by the model after the input tokens
    if model_name in ['gpt2', 'llama-3b', 'llama-7b', 'falcon-7b-instruct', 'llama2']:
        decoded_outputs = tokenizer.batch_decode(outputs[:, input_ids.size(1):], skip_special_tokens=True)
    else:
        decoded_outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    return decoded_outputs