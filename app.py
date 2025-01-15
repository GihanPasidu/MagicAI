# Ensure you have the transformers library installed
# You can install it using the following command:
# pip install transformers

import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize tokenizer and model with CodeBERT
MODEL_NAME = "microsoft/CodeBERT-base"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
except Exception as e:
    logging.error(f"Failed to load model: {e}")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    # Render the main webpage
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get the input from the frontend
        data = request.json
        prompt = data.get("prompt", "")
        logging.debug(f"Received prompt: {prompt}")

        # Format prompt for code generation
        formatted_prompt = f"Generate code for: {prompt}\nAnswer:"

        # Generate response with better parameters
        inputs = tokenizer(formatted_prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs["input_ids"],
            max_length=200,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        logging.debug(f"Model outputs: {outputs}")

        # Decode and clean response
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = response_text.replace(formatted_prompt, "").strip()
        logging.debug(f"Generated response: {response_text}")

        # Return the generated text
        return jsonify({"response_text": response_text})

    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    try:
        model_name = "t5-small"
        model_version = "1.0.0"  # Example version
        model_description = "A small version of the T5 model for text generation."
        return jsonify({"name": model_name, "version": model_version, "description": model_description})
    except Exception as e:
        logging.error(f"Error fetching model info: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
