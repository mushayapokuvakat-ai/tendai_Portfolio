from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import statistics as stats_lib

from sympy import (
    symbols, sympify, solve, simplify, diff, integrate,
    trigsimp, series, Matrix, latex, factor, expand,
    sin, cos, tan, pi, E, sqrt, log, Abs,
    limit, oo, Rational
)
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import scipy.stats as sci_stats

app = Flask(__name__, static_url_path='', static_folder='..')
CORS(app)

x, y, z, n, a, b, t = symbols('x y z n a b t')

TRANSFORMS = (standard_transformations + (implicit_multiplication_application,))

def safe_parse(expr_str):
    expr_str = expr_str.replace('^', '**')
    return parse_expr(expr_str, transformations=TRANSFORMS)

# ─────────────────────────────────────────────────────────────
# MODULE 1: PURE MATHEMATICS ENGINE
# ─────────────────────────────────────────────────────────────

def engine_differentiate(expr_str, var_str='x'):
    sym = symbols(var_str)
    expr = safe_parse(expr_str)
    result = diff(expr, sym)
    steps = [
        f"📌 Expression: f({var_str}) = {expr}",
        f"📐 Applying differentiation rules to each term...",
        f"✅ d/d{var_str} [{expr}] = {result}",
        f"📝 Simplified: {simplify(result)}"
    ]
    return {"answer": str(simplify(result)), "steps": steps}

def engine_integrate(expr_str, var_str='x', lower=None, upper=None):
    sym = symbols(var_str)
    expr = safe_parse(expr_str)
    if lower is not None and upper is not None:
        result = integrate(expr, (sym, lower, upper))
        steps = [
            f"📌 Expression: f({var_str}) = {expr}",
            f"📐 Computing definite integral from {lower} to {upper}...",
            f"∫ [{expr}] d{var_str} from {lower} to {upper}",
            f"✅ Result = {simplify(result)}"
        ]
    else:
        result = integrate(expr, sym)
        steps = [
            f"📌 Expression: f({var_str}) = {expr}",
            f"📐 Applying integration rules to each term...",
            f"✅ ∫ [{expr}] d{var_str} = {result} + C",
        ]
    return {"answer": str(simplify(result)), "steps": steps}

def engine_solve_equation(equation_str):
    try:
        if '=' in equation_str:
            lhs_s, rhs_s = equation_str.split('=', 1)
            lhs = safe_parse(lhs_s)
            rhs = safe_parse(rhs_s)
            expr = lhs - rhs
        else:
            expr = safe_parse(equation_str)
        result = solve(expr, x)
        steps = [
            f"📌 Equation: {equation_str}",
            f"📐 Rearranging to: {simplify(expr)} = 0",
            f"🔍 Solving for x...",
            f"✅ x = {result}"
        ]
        return {"answer": str(result), "steps": steps}
    except Exception as e:
        return {"error": str(e), "steps": [f"❌ Could not parse: {equation_str}"]}

def engine_simplify(expr_str):
    expr = safe_parse(expr_str)
    result = simplify(expr)
    steps = [
        f"📌 Expression: {expr}",
        f"📐 Applying algebraic simplification...",
        f"✅ Simplified: {result}"
    ]
    return {"answer": str(result), "steps": steps}

def engine_factor(expr_str):
    expr = safe_parse(expr_str)
    result = factor(expr)
    steps = [
        f"📌 Expression: {expr}",
        f"📐 Factorising...",
        f"✅ Factored form: {result}"
    ]
    return {"answer": str(result), "steps": steps}

# ─────────────────────────────────────────────────────────────
# MODULE 2: STATISTICS ENGINE
# ─────────────────────────────────────────────────────────────

def parse_list(query):
    nums = re.findall(r'[-+]?\d*\.?\d+', query)
    return [float(n) for n in nums]

def engine_statistics(query, operation):
    data = parse_list(query)
    if not data:
        return {"error": "No numbers found in input.", "steps": []}
    n_val = len(data)
    steps = [f"📌 Data: {data}", f"📊 n = {n_val}"]
    result = None

    if operation == 'mean':
        result = stats_lib.mean(data)
        steps += [
            f"📐 Formula: Mean = Σx / n",
            f"📐 Sum = {sum(data)}",
            f"✅ Mean = {sum(data)} / {n_val} = {result:.4f}"
        ]
    elif operation == 'median':
        result = stats_lib.median(data)
        sorted_d = sorted(data)
        steps += [
            f"📐 Sorted: {sorted_d}",
            f"✅ Median = {result}"
        ]
    elif operation == 'mode':
        try:
            result = stats_lib.mode(data)
            steps += [f"✅ Mode = {result}"]
        except Exception:
            result = "No unique mode"
            steps += [f"✅ {result}"]
    elif operation == 'variance':
        result = stats_lib.variance(data)
        mean_v = stats_lib.mean(data)
        steps += [
            f"📐 Formula: Variance = Σ(x - mean)² / (n - 1)",
            f"📐 Mean = {mean_v:.4f}",
            f"✅ Variance = {result:.4f}"
        ]
    elif operation == 'std' or operation == 'stdev' or operation == 'standard deviation':
        result = stats_lib.stdev(data)
        steps += [
            f"📐 Formula: Std Dev = √Variance",
            f"📐 Variance = {stats_lib.variance(data):.4f}",
            f"✅ Standard Deviation = {result:.4f}"
        ]
    elif operation == 'range':
        result = max(data) - min(data)
        steps += [
            f"📐 Formula: Range = Max − Min",
            f"📐 Max = {max(data)}, Min = {min(data)}",
            f"✅ Range = {result}"
        ]
    elif operation == 'quartile' or operation == 'iqr':
        q1 = sci_stats.scoreatpercentile(data, 25)
        q3 = sci_stats.scoreatpercentile(data, 75)
        iqr = q3 - q1
        result = iqr
        steps += [
            f"📐 Q1 (25th percentile) = {q1}",
            f"📐 Q3 (75th percentile) = {q3}",
            f"✅ IQR = Q3 − Q1 = {iqr}"
        ]
    elif operation == 'correlation' or operation == 'r':
        if len(data) < 4:
            return {"error": "Need at least two datasets (4 numbers min)", "steps": []}
        mid = len(data) // 2
        x_data = data[:mid]
        y_data = data[mid:]
        r, p = sci_stats.pearsonr(x_data, y_data)
        result = r
        steps += [
            f"📐 X values: {x_data}",
            f"📐 Y values: {y_data}",
            f"📐 Pearson correlation formula applied",
            f"✅ r = {r:.4f}, p-value = {p:.4f}"
        ]
    return {"answer": f"{result}", "steps": steps}

# ─────────────────────────────────────────────────────────────
# MODULE 3: FUNCTION POINT ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────

FP_WEIGHTS = {
    'EI':  {'low': 3, 'avg': 4, 'high': 6},
    'EO':  {'low': 4, 'avg': 5, 'high': 7},
    'EQ':  {'low': 3, 'avg': 4, 'high': 6},
    'ILF': {'low': 7, 'avg': 10, 'high': 15},
    'EIF': {'low': 5, 'avg': 7,  'high': 10},
}

def engine_function_points(components, vaf_sum=None):
    """
    components: list of {'type': 'EI', 'complexity': 'low', 'count': 3}
    vaf_sum: integer sum of all Fi values (0-70 range, 14 factors × 0-5)
    Formula: FP = Count Total × [0.65 + 0.01 × ∑(Fi)]
    """
    steps = ["📌 Function Point Analysis (IFPUG Method)"]
    steps.append("\n🔢 Step 1 — Calculate Unadjusted Function Points (UFP):")
    steps.append(f"{'Component':<10} {'Complexity':<12} {'Count':<8} {'Weight':<8} {'UFP'}")
    steps.append("-" * 55)

    total_ufp = 0
    for comp in components:
        ctype = comp.get('type', '').upper()
        complexity = comp.get('complexity', 'avg').lower()
        count = int(comp.get('count', 1))
        weight = FP_WEIGHTS.get(ctype, {}).get(complexity, 0)
        subtotal = count * weight
        total_ufp += subtotal
        steps.append(f"{ctype:<10} {complexity:<12} {count:<8} {weight:<8} {subtotal}")

    steps.append(f"\n✅ Total UFP (Count Total) = {total_ufp}")

    if vaf_sum is not None:
        fi_sum = vaf_sum
    else:
        fi_sum = 35  # Default: moderate (14 factors × 2.5 avg)

    vaf = 0.65 + 0.01 * fi_sum
    fp = total_ufp * vaf

    steps += [
        f"\n🔢 Step 2 — Calculate Value Adjustment Factor (VAF):",
        f"   ∑(Fi) = {fi_sum}  (sum of 14 General System Characteristics, each 0–5)",
        f"   VAF = 0.65 + (0.01 × {fi_sum}) = {vaf:.4f}",
        f"\n🔢 Step 3 — Apply FP Formula:",
        f"   FP = Count Total × [0.65 + 0.01 × ∑(Fi)]",
        f"   FP = {total_ufp} × {vaf:.4f}",
        f"\n✅ Final Function Points (FP) = {fp:.2f}"
    ]

    return {
        "ufp": total_ufp,
        "vaf": round(vaf, 4),
        "fi_sum": fi_sum,
        "fp": round(fp, 2),
        "steps": steps
    }

# ─────────────────────────────────────────────────────────────
# MODULE 4: COCOMO ENGINE
# ─────────────────────────────────────────────────────────────

COCOMO_PARAMS = {
    'organic':       {'a': 2.4,  'b': 1.05, 'c': 2.5, 'd': 0.38},
    'semi-detached': {'a': 3.0,  'b': 1.12, 'c': 2.5, 'd': 0.35},
    'embedded':      {'a': 3.6,  'b': 1.20, 'c': 2.5, 'd': 0.32},
}

def engine_cocomo(kloc, mode='organic'):
    mode = mode.lower().strip()
    if mode not in COCOMO_PARAMS:
        mode = 'organic'
    p = COCOMO_PARAMS[mode]
    effort = p['a'] * (kloc ** p['b'])
    duration = p['c'] * (effort ** p['d'])
    staff = effort / duration
    productivity = kloc / effort

    steps = [
        f"📌 COCOMO Model — Mode: {mode.title()}",
        f"📐 KLOC (Thousands of Lines of Code) = {kloc}",
        f"\n🔢 Step 1 — Effort Estimation:",
        f"   Formula: E = a × (KLOC)^b",
        f"   E = {p['a']} × ({kloc})^{p['b']}",
        f"   E = {p['a']} × {round(kloc ** p['b'], 4)}",
        f"   ✅ Effort (E) = {effort:.2f} Person-Months",
        f"\n🔢 Step 2 — Development Duration:",
        f"   Formula: D = c × (E)^d",
        f"   D = {p['c']} × ({effort:.2f})^{p['d']}",
        f"   ✅ Duration (D) = {duration:.2f} Months",
        f"\n🔢 Step 3 — Staff Required:",
        f"   Formula: Staff = E / D",
        f"   Staff = {effort:.2f} / {duration:.2f}",
        f"   ✅ Staff = {staff:.2f} People",
        f"\n🔢 Step 4 — Productivity:",
        f"   Formula: Productivity = KLOC / E",
        f"   Productivity = {kloc} / {effort:.2f}",
        f"   ✅ Productivity = {productivity:.4f} KLOC/Person-Month",
    ]
    return {
        "effort": round(effort, 2),
        "duration": round(duration, 2),
        "staff": round(staff, 2),
        "productivity": round(productivity, 4),
        "mode": mode,
        "steps": steps
    }

# ─────────────────────────────────────────────────────────────
# INTELLIGENT QUERY ROUTER
# ─────────────────────────────────────────────────────────────

def route_query(query):
    q = query.strip()
    ql = q.lower()

    # --- COCOMO ---
    if 'cocomo' in ql:
        nums = re.findall(r'\d+\.?\d*', q)
        kloc = float(nums[0]) if nums else 10
        mode = 'organic'
        if 'semi' in ql or 'semi-detached' in ql:
            mode = 'semi-detached'
        elif 'embedded' in ql:
            mode = 'embedded'
        result = engine_cocomo(kloc, mode)
        return "\n".join(result['steps'])

    # --- FUNCTION POINTS ---
    if 'function point' in ql or ' fp ' in ql or ql.startswith('fp'):
        components = []
        vaf_sum = None
        for ctype in ['EI', 'EO', 'EQ', 'ILF', 'EIF']:
            pattern = rf'(\d+)\s*{ctype}\s*(low|avg|high)?'
            matches = re.findall(pattern, q, re.IGNORECASE)
            for m in matches:
                count = int(m[0])
                complexity = m[1].lower() if m[1] else 'avg'
                components.append({'type': ctype, 'complexity': complexity, 'count': count})
        vaf_match = re.search(r'vaf\s*[=:]?\s*(\d+)', ql)
        fi_match = re.search(r'fi\s*[=:]?\s*(\d+)', ql)
        if vaf_match:
            vaf_sum = int(vaf_match.group(1))
        elif fi_match:
            vaf_sum = int(fi_match.group(1))
        if not components:
            return ("❓ Please specify components like: '3 EI low, 2 ILF avg, VAF=42'\n"
                    "Components: EI, EO, EQ, ILF, EIF. Complexity: low/avg/high.")
        result = engine_function_points(components, vaf_sum)
        return "\n".join(result['steps'])

    # --- STATISTICS ---
    stat_ops = {
        'mean': 'mean', 'average': 'mean',
        'median': 'median',
        'mode': 'mode',
        'variance': 'variance',
        'standard deviation': 'std', 'std dev': 'std', 'stdev': 'std', 'std': 'std',
        'range': 'range',
        'iqr': 'iqr', 'quartile': 'quartile',
        'correlation': 'correlation', 'pearson': 'correlation'
    }
    for keyword, op in stat_ops.items():
        if keyword in ql:
            result = engine_statistics(q, op)
            if 'error' in result:
                return f"❌ Error: {result['error']}"
            return "\n".join(result['steps'])

    # --- PURE MATHS: Differentiation ---
    if any(k in ql for k in ['differentiate', 'derivative', 'diff', 'd/dx', "f'(x)"]):
        expr_match = re.search(r'(?:differentiate|derivative of|diff)\s+(.+?)(?:\s+with respect to \w+)?$', ql)
        expr_str = expr_match.group(1) if expr_match else q
        var_match = re.search(r'with respect to (\w)', ql)
        var = var_match.group(1) if var_match else 'x'
        result = engine_differentiate(expr_str.strip(), var)
        return "\n".join(result['steps'])

    # --- PURE MATHS: Integration ---
    if any(k in ql for k in ['integrate', 'integral', '∫']):
        definite = re.search(r'from\s+(-?\d+\.?\d*)\s+to\s+(-?\d+\.?\d*)', ql)
        expr_match = re.search(r'(?:integrate|integral of)\s+(.+?)(?:\s+from)?', ql)
        expr_str = expr_match.group(1).strip() if expr_match else q
        if definite:
            lo, hi = float(definite.group(1)), float(definite.group(2))
            result = engine_integrate(expr_str, lower=lo, upper=hi)
        else:
            result = engine_integrate(expr_str)
        return "\n".join(result['steps'])

    # --- PURE MATHS: Solve equation ---
    if any(k in ql for k in ['solve', 'find x', 'find the value']) or '=' in q:
        expr_str = re.sub(r'^(solve|find x|find the value of x)[:\s]*', '', ql).strip()
        if not expr_str:
            expr_str = q
        result = engine_solve_equation(expr_str)
        return "\n".join(result['steps'])

    # --- PURE MATHS: Factorise ---
    if any(k in ql for k in ['factor', 'factorise', 'factorize']):
        expr_str = re.sub(r'^(factor|factorise|factorize)[:\s]*', '', ql).strip()
        result = engine_factor(expr_str or q)
        return "\n".join(result['steps'])

    # --- PURE MATHS: Simplify ---
    if 'simplify' in ql:
        expr_str = re.sub(r'^simplify[:\s]*', '', ql).strip()
        result = engine_simplify(expr_str or q)
        return "\n".join(result['steps'])

    # --- FALLBACK: try to evaluate raw math ---
    if re.search(r'[\d\+\-\*\/\^\(\)xX]', q):
        try:
            if '=' in q:
                result = engine_solve_equation(q)
            else:
                result = engine_simplify(q)
            return "\n".join(result['steps'])
        except Exception:
            pass

    # --- DEFAULT RESPONSE ---
    return (
        "👋 Hi! I'm Tendai's AI Math Tutor. I can help with:\n\n"
        "🔢 **Pure Maths**: differentiate x^3+2x | integrate sin(x) | solve x^2-4=0 | simplify (x+1)^2 | factorise x^2-5x+6\n"
        "📊 **Statistics**: mean of [4,6,8,10] | standard deviation of [2,4,4,4,5,5,7,9]\n"
        "🖥️ **Function Points**: 3 EI low, 2 ILF avg, 1 EO high, VAF=42\n"
        "📐 **COCOMO**: COCOMO 15 KLOC organic | COCOMO 50 KLOC embedded\n"
        "🎓 **About Patnat Academy**: What is Patnat Academy?\n\n"
        "Try any of the above!"
    )

# ─────────────────────────────────────────────────────────────
# FLASK ROUTES
# ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '')
    response = route_query(user_message)
    return jsonify({"response": response})

@app.route('/api/solve', methods=['POST'])
def api_solve():
    data = request.json or {}
    mode = data.get('mode', 'math')
    if mode == 'fp':
        components = data.get('components', [])
        vaf_sum = data.get('vaf_sum', None)
        result = engine_function_points(components, vaf_sum)
    elif mode == 'cocomo':
        kloc = float(data.get('kloc', 10))
        cocomo_mode = data.get('cocomo_mode', 'organic')
        result = engine_cocomo(kloc, cocomo_mode)
    elif mode == 'stat':
        operation = data.get('operation', 'mean')
        query = data.get('query', '')
        result = engine_statistics(query, operation)
    else:
        equation = data.get('equation', '')
        result = engine_solve_equation(equation)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "engine": "AI Math Engine v2"})

if __name__ == '__main__':
    print("AI Math Engine v2 - running on http://localhost:5000")
    app.run(port=5000, debug=True)
