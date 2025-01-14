# Ensure you have the transformers library installed
# You can install it using the following command:
# pip install transformers

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModelForSeq2SeqLM.from_pretrained("microsoft/codebert-base")

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

        # Encode the input and generate a response using CodeBERT
        inputs = tokenizer.encode(prompt, return_tensors='pt')
        outputs = model.generate(inputs, max_length=200)

        # Decode the generated response
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Return the generated text
        return jsonify({"response": response_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
