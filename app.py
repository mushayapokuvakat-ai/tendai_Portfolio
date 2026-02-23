from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for frontend communication

@app.route('/')
def index():
    return app.send_static_file('index.html')

from sympy import sympify, solve, symbols, simplify, diff, integrate, latex
import sympy

# Advanced Math Solver Logic
def solve_math_problem(problem):
    try:
        # Check if it's an equation with '='
        if '=' in problem:
            lhs_str, rhs_str = problem.split('=')
            lhs = sympify(lhs_str)
            rhs = sympify(rhs_str)
            # Find the variable to solve for (usually x)
            var = symbols('x')
            result = solve(lhs - rhs, var)
            return {
                "type": "equation",
                "solution": [str(res) for res in result] if result else "No solution found",
                "steps": [f"Equation: {lhs_str} = {rhs_str}", f"Simplified LHS - RHS: {simplify(lhs - rhs)} = 0"]
            }
        else:
            # Try to simplify expression
            expr = sympify(problem)
            return {
                "type": "expression",
                "simplified": str(simplify(expr)),
                "derivative": str(diff(expr, symbols('x'))),
                "integral": str(integrate(expr, symbols('x')))
            }
    except Exception as e:
        return {"error": str(e)}

# Mock AI Chat Logic (Enhanced)
def get_ai_response(query):
    query_clean = query.lower().strip()
    
    # Check if there's a math expression (basic heuristic)
    math_symbols = ['+', '-', '*', '/', '^', '=', 'sqrt', 'log', 'sin', 'cos']
    if any(symbol in query for symbol in math_symbols):
        # Extract expression - this is a simple extraction, could be improved
        parts = query.split()
        for p in parts:
            if any(s in p for s in math_symbols):
                math_result = solve_math_problem(p)
                if "error" not in math_result:
                    if math_result['type'] == 'equation':
                        return f"I solved that equation for you! The solution is: {math_result['solution']}. My logic: {math_result['steps'][1]}."
                    else:
                        return f"I simplified that for you: {math_result['simplified']}. Derivative: {math_result['derivative']}."
    
    if 'math' in query_clean or 'equation' in query_clean:
        return "I'm ready! Send me any equation (like 'x^2 - 4 = 0') or expression and I'll solve it for you using my new SymPy engine."
    elif 'patnat' in query_clean or 'academy' in query_clean:
        return "Patnat Academy is Tendai's platform for high-level STEM mentorship. We specialize in making advanced math accessible."
    else:
        return "I can help with math, programming, or info about Tendai's projects. Try asking me to solve an equation!"

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
    result = solve_math_problem(equation)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    print("Tendai's Portfolio Backend running on http://localhost:5000")
    app.run(port=5000, debug=True)
