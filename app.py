from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for frontend communication

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Mock AI Chat Logic
def get_ai_response(query):
    query = query.lower()
    if 'math' in query or 'equation' in query:
        return "I can help you with that! Are you looking for a step-by-step solution to a specific problem?"
    elif 'patnat' in query or 'academy' in query:
        return "Patnat Academy is Tendai's innovative learning platform. We offer courses in Mathematics and Computing."
    elif 'help' in query:
        return "I can assist with Calculus, Algebra, Statistics, and Software Engineering queries. What's on your mind?"
    else:
        return f"That sounds interesting! As an AI trained by Tendai, I'd suggest looking into how {query} relates to mathematical logic."

# Basic Math Solver Logic
def solve_equation(equation):
    # Simulated solver for basic linear/quadratic patterns
    # In a real app, you might use SymPy
    try:
        if 'x' in equation:
            return {
                "equation": equation,
                "steps": [
                    f"1. Identify the variable: x",
                    f"2. Rearrange the equation: {equation}",
                    "3. Apply algebraic properties to isolate x.",
                    "4. Final Solution: x = [Calculated Value]"
                ],
                "result": "Solution found via algebraic isolation."
            }
        return {"error": "Equation pattern not recognized. Please try a simpler linear form."}
    except Exception as e:
        return {"error": str(e)}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    response = get_ai_response(user_message)
    return jsonify({"response": response})

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.json
    equation = data.get('equation', '')
    result = solve_equation(equation)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    print("Tendai's Portfolio Backend running on http://localhost:5000")
    app.run(port=5000, debug=True)
