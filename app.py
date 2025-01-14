from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# OpenAI API Key (replace with your key)
openai.api_key = "your_openai_api_key"

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

        # Generate response using OpenAI's GPT model
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200,
            temperature=0.5
        )

        # Return the generated text
        return jsonify({"response": response.choices[0].text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
