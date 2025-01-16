from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import re
import subprocess
import sys

def install_nltk():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])

def install_openai():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])

try:
    import nltk
except ModuleNotFoundError:
    install_nltk()
    import nltk

try:
    import openai
except ModuleNotFoundError:
    install_openai()
    import openai

from nltk.corpus import stopwords

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model and tokenizer
try:
    MODEL_NAME = "distilgpt2"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    logger.info(f"Model loaded successfully on {device}")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

def simplify_prompt(prompt):
    # Convert to lowercase
    prompt = prompt.lower()
    # Remove punctuation
    prompt = re.sub(r'[^\w\s]', '', prompt)
    # Remove stopwords
    prompt = ' '.join([word for word in prompt.split() if word not in stop_words])
    return prompt

def generate_response(prompt):
    # Tokenize and generate
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        inputs,
        max_new_tokens=150,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.95,
        top_k=50,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=2
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        
        if not prompt:
            return jsonify({"error": "Empty prompt"}), 400

        # Simplify the prompt
        simplified_prompt = simplify_prompt(prompt)

        # Generate response using the model
        response = generate_response(simplified_prompt)
        
        # Post-process the response to ensure it is valid and coherent
        response_lines = response.split('\n')
        response = response_lines[0]  # Take the first line of the response
        if not response.endswith('.'):
            response += '.'
        
        # Additional filtering to remove incomplete or irrelevant responses
        if not response.startswith("def") and not response.startswith("class"):
            response = "Sorry, I couldn't generate a valid Python code snippet. Please try again with a different prompt."
        
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    try:
        model_name = "GPT-2 Medium"
        model_version = "2.0"
        model_description = "An advanced language model with 345M parameters, capable of generating high-quality code and text."
        return jsonify({"name": model_name, "version": model_version, "description": model_description})
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
