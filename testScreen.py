from flask import Flask, request, session, jsonify, render_template
from waitress import serve
from datetime import datetime
import uuid

from access_logger import AccessLogger  # Si lo pones en otro archivo, si no, ignora esta línea

# Flask app
app = Flask(__name__)
#md5 juan
app.secret_key = 'a94652aa97c7211ba8954dd15a3cf838'

access_logger = AccessLogger()  # Instancia global

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    session_id = session['session_id']

    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Registrar acceso usando la clase
    access_logger.log_access(session_id, ip, user_agent, now)
    # Imprimir en consola
    print(f"[{now}] GET / from {ip} | Session: {session_id} | User-Agent: {user_agent}")

    # Renderizar una plantilla HTML simple
    return render_template('index.html')

@app.route('/user_aliases')
def user_aliases():
    # Supón que access_logger tiene un método get_user_aliases() que devuelve una lista o dict
    aliases = access_logger.get_all_user_aliases()  # Debes implementar este método en AccessLogger
    return jsonify(aliases)

@app.route('/access_history')
def access_history():
    # Supón que access_logger tiene un método get_access_history() que devuelve una lista de accesos
    history = access_logger.get_access_history(limit=20)  # Devuelve los últimos 20 accesos
    return jsonify(history)

@app.route('/set_alias', methods=['POST'])
def set_alias():
    if 'session_id' not in session:
        return jsonify({"error": "No session found"}), 400
    data = request.get_json()
    alias = data.get('alias')
    if not alias:
        return jsonify({"error": "Alias is required"}), 400
    session_id = session['session_id']
    access_logger.set_user_alias(session_id, alias)
    return jsonify({"success": True, "session_id": session_id, "alias": alias})

serve(app, host='0.0.0.0', port=5000)