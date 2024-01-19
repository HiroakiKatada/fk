import os
from flask import Flask, request, render_template_string, session
from flask_session import Session

# Settings
app = Flask(__name__)
app.config['SESSION_KEY'] = os.environ.get('SESSION_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Template
html_template = '''
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Diagnostic Tool</title>
</head>
<body>
    <h2>{{ question }}</h2>
    <form method='post' action='/question'>
        <input type='radio' id='yes' name='answer' value='yes' required>
        <label for='yes'>Yes</label><br>
        <input type='radio' id='no' name='answer' value='no' required>
        <label for='no'>No</label><br>
        <input type='hidden' name='current_step' value='{{ current_step }}'>
        <input type='submit' value='Submit'>
    </form>
</body>
</html>
'''

# Questions
question_flow = {
    'start': ('ご当地キャラのグッズですか？', '5', 'concierege'),
    'concierege': ('コンシェルジュ、後から寄附？', '99', 'ticket'),
    'ticket': ('チケット、券類ですか？', 'multi_exchange', 'aged_rice'),
    'multi_exchange': ('引き換えるものが複数に渡りますか？', '99', '7'),
    'aged_rice': ('熟成肉 or 精米ですか？', 'local_production_aged', 'attached_items'),
    'local_production_aged': ('原材料は区域内産ですか？', '1', 'prefecture_production_aged'),
    'prefecture_production_aged': ('区域が属する都道府県内産ですか？', 'local_production_aged2', 'error'),
    'local_production_aged2': ('区域内で熟成 or 精米されますか？', '3', 'error'),
    'attached_items': ('付帯物がありますか？', 'main_value', 'processed_food'),
    'main_value': ('主体の価値（価格や重さ）は全体の70%以上ありますか？', 'main_local', 'error'),
    'main_local': ('主体は区域内で作られますか？', '6', 'error'),
    'processed_food': ('食品ですか？', 'processed_product', 'non_food'),
    'processed_product': ('加工品ですか？', 'local_processing_food', '1'),
    'local_processing_food': ('区域内加工ですか？', '3', 'local_material_food'),
    'local_material_food': ('原材料は区域内生産ですか？', 'majority_weight_price', 'error'),
    'majority_weight_price': ('重さ or 価格が全体の90%以上ですか？', '2', 'inquiry'),
    'non_food': ('区域内加工ですか？', '3', 'local_material_non_food'),
    'local_material_non_food': ('原材料は区域内生産ですか？', 'non_food_majority_weight_price', 'error'),
    'non_food_majority_weight_price': ('重さ or 価格が全体の90%以上ですか？', '2', 'inquiry'),
    'error': ('Error', None, None),
    'inquiry': ('要問い合わせ', None, None)
}

@app.route('/', methods=['GET'])
def index():
    session.clear()
    question, _, _ = question_flow['start']
    return render_template_string(html_template, question=question, current_step='start', history=[])

@app.route('/question', methods=['POST'])
def question():
    answer = request.form.get('answer')
    current_step = request.form.get('current_step')
    history = request.form.getlist('history')

    # Add current step to history
    if current_step != 'start':
        history.append(current_step)

    if answer == 'yes':
        next_step = question_flow[current_step][1]
    else:
        next_step = question_flow[current_step][2]

    if next_step.isdigit() or next_step in ['Error', '要問い合わせ', '99']:
        return f'Result: {next_step}'
    else:
        next_question, _, _ = question_flow[next_step]
        return render_template_string(html_template, question=next_question, current_step=next_step, history=history)

@app.route('/back', methods=['POST'])
def back():
    history = request.form.getlist('history')
    if not history:
        return index()
    last_step = history.pop()
    question, _, _ = question_flow[last_step]
    return render_template_string(html_template, question=question, current_step=last_step, history=history)


if __name__ == '__main__':
    app.run(debug=True)
