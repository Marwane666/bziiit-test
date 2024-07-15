from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from .initialization import initialize_and_persist_vectorstore, evaluate_answers_with_chat_engine
import llama_index.core.chat_engine.types
import json
import os

main = Blueprint('main', __name__)

# Chemins vers les répertoires nécessaires
dir_path = "data"  # Chemin vers votre répertoire contenant les textes du PDF
persist_dir = "./storage1"  # Chemin vers votre répertoire de persistance

# Initialisation du moteur de chat
chat_engine = initialize_and_persist_vectorstore(dir_path, persist_dir)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')
@main.route('/documentation')
def documentation():
    return render_template('documentation.html')

@main.route('/questions')
def questions():
    return render_template('questions.html')

@main.route('/training_plan')
def training_plan():
    try:
        with open('answers.json', 'r', encoding='utf-8') as f:
            answers = json.load(f)
        training_plan = evaluate_answers_with_chat_engine(chat_engine, answers)
        return render_template('training_plan.html', training_plan=training_plan)
    except Exception as e:
        print(f"Error in /training_plan: {e}")
        return "An error occurred while generating the training plan. Please try again later.", 500


@main.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    print("Received message:", message)
    
    response = chat_engine.chat(message)
    print(response)
    print("Type of response:", type(response))
    
    if isinstance(response, llama_index.core.chat_engine.types.AgentChatResponse):
        response_data = {
            'response': response.response,
        }
    else:
        response_data = str(response)
    
    return jsonify(response_data)

@main.route('/generate_questions', methods=['POST'])
def generate_questions():
    data = request.get_json()
    num_questions = data.get('num_questions', 10)
    prompt = f"Tu me génère {num_questions} questions pour évaluer l’utilisateur sur ses connaissances du document, en restant resreint au contexte, les questions doivent contenir (l'id de la question, la question et les éléments de réponse[en sous-éléments], non pas les choix comme un qcm). format json brut"
    response = chat_engine.chat(prompt)
    questions = json.loads(response.response)  # Ensure the response is parsed into a dictionary
    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=4, ensure_ascii=False)
    return jsonify({'status': 'success', 'questions': questions})

@main.route('/submit_answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    answers = data.get('answers')

    with open('answers.json', 'w', encoding='utf-8') as f:
        json.dump(answers, f, indent=4, ensure_ascii=False)

    return redirect(url_for('main.evaluation'))

@main.route('/evaluation')
def evaluation():
    try:
        with open('answers.json', 'r', encoding='utf-8') as f:
            answers = json.load(f)
        training_plan = evaluate_answers_with_chat_engine(chat_engine, answers)
        return render_template('training_plan.html', training_plan=training_plan)
    except Exception as e:
        print(f"Error in /evaluation: {e}")
        return "An error occurred while generating the evaluation. Please try again later.", 500


