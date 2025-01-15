from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model and tokenizer
try:
    MODEL_NAME = "microsoft/CodeGPT-small-py"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    logger.info(f"Model loaded successfully on {device}")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

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

        # Tokenize and generate
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            inputs,
            max_length=150,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.95,
            top_k=50,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=2
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
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
