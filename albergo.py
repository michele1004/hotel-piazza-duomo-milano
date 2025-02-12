// Importiamo i moduli necessari

from flask import Flask, request, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Creiamo l'applicazione Flask
app = Flask(__name__)

// Configurazione del database (usiamo SQLite per semplicità)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prenotazioni.db'
app.config['SECRET_KEY'] = 'una_chiave_segreta_per_i_messaggi_flash'  // Necessaria per i messaggi flash
db = SQLAlchemy(app)

// Definiamo il modello per le prenotazioni
class Prenotazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificativo unico della prenotazione
    nome_cliente = db.Column(db.String(100), nullable=False)  // Nome e cognome del cliente
    email_cliente = db.Column(db.String(100), nullable=False, unique=True)  // Email del cliente (unica)
    tipo_stanza = db.Column(db.String(50), nullable=False)  // Tipo di stanza selezionata
    data_checkin = db.Column(db.String(20), nullable=False)  // Data di check-in
    data_checkout = db.Column(db.String(20), nullable=False)  // Data di check-out

    def __repr__(self):
        return f"Prenotazione di {self.nome_cliente} - Stanza: {self.tipo_stanza}"

// Funzione per inizializzare il database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database inizializzato!")

// Pagina principale per la prenotazione
@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Albergo - Prenota la tua stanza</title>
        </head>
        <body>
            <h1>Benvenuti all'Albergo!</h1>
            <p>Prenota la tua stanza per un'esperienza indimenticabile.</p>

            <!-- Mostra eventuali messaggi flash -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <ul>
                        {% for category, message in messages %}
                            <li style="color: {{ 'green' if category == 'success' else 'red' }};">{{ message }}</li>
                        {% endfor %}
                    </ul>
                {% endif %}
            {% endwith %}

            <form action="/prenota" method="POST">
                <label for="nome">Nome e Cognome:</label><br>
                <input type="text" id="nome" name="nome" required><br><br>
                
                <label for="email">Email:</label><br>
                <input type="email" id="email" name="email" required><br><br>
                
                <label for="tipo_stanza">Tipo di Stanza:</label><br>
                <select id="tipo_stanza" name="tipo_stanza" required>
                    <option value="">Seleziona...</option>
                    <option value="Singola">Singola</option>
                    <option value="Doppia">Doppia</option>
                    <option value="Tripla">Tripla</option>
                    <option value="Suite">Suite</option>
                </select><br><br>
                
                <label for="checkin">Data Check-in:</label><br>
                <input type="date" id="checkin" name="checkin" required><br><br>
                
                <label for="checkout">Data Check-out:</label><br>
                <input type="date" id="checkout" name="checkout" required><br><br>
                
                <input type="checkbox" id="privacy" name="privacy" required>
                <label for="privacy">Accetto il trattamento dei dati personali e la privacy policy.</label><br><br>
                
                <button type="submit">Prenota</button>
            </form>

            <p><a href="{{ url_for('cancella_form') }}">Cancella una prenotazione</a></p>
        </body>
        </html>
    ''')

// Gestione della prenotazione
@app.route('/prenota', methods=['POST'])
def prenota():
    try:
        // Otteniamo i dati dal form
        nome = request.form['nome']
        email = request.form['email']
        tipo_stanza = request.form['tipo_stanza']
        data_checkin = request.form['checkin']
        data_checkout = request.form['checkout']

        // Verifichiamo che le date siano coerenti
        if data_checkin >= data_checkout:
            flash("Errore: La data di check-out deve essere successiva a quella di check-in.", "error")
            return redirect(url_for('index'))

        // Verifichiamo se l'email è già stata usata
        if Prenotazione.query.filter_by(email_cliente=email).first():
            flash("Errore: Questa email è già associata a una prenotazione esistente.", "error")
            return redirect(url_for('index'))

        // Creiamo una nuova prenotazione
        nuova_prenotazione = Prenotazione(
            nome_cliente=nome,
            email_cliente=email,
            tipo_stanza=tipo_stanza,
            data_checkin=data_checkin,
            data_checkout=data_checkout
        )

        // Salviamo la prenotazione nel database
        db.session.add(nuova_prenotazione)
        db.session.commit()

        // Mostriamo un messaggio di conferma
        flash(f"Grazie {nome}, la tua stanza è stata prenotata con successo!", "success")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Si è verificato un errore durante la prenotazione: {str(e)}", "error")
        return redirect(url_for('index'))

// Gestione della cancellazione di una prenotazione
@app.route('/cancella', methods=['POST'])
def cancella():
    try:
        // Otteniamo l'email dal form
        email = request.form['email']

        // Cerchiamo la prenotazione corrispondente
        prenotazione = Prenotazione.query.filter_by(email_cliente=email).first()

        if not prenotazione:
            flash("Nessuna prenotazione trovata con questa email.", "error")
            return redirect(url_for('cancella_form'))

        // Cancelliamo la prenotazione
        db.session.delete(prenotazione)
        db.session.commit()

        // Mostriamo un messaggio di conferma
        flash(f"La prenotazione associata all'email {email} è stata cancellata con successo.", "success")
        return redirect(url_for('cancella_form'))
    except Exception as e:
        flash(f"Si è verificato un errore durante la cancellazione: {str(e)}", "error")
        return redirect(url_for('cancella_form'))

// Pagina per cancellare una prenotazione
@app.route('/cancella-prenotazione')
def cancella_form():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <title>Albergo - Cancella Prenotazione</title>
        </head>
        <body>
            <h1>Cancella una Prenotazione</h1>
            <p>Inserisci l'email associata alla prenotazione che vuoi cancellare.</p>

            <!-- Mostra eventuali messaggi flash -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <ul>
                        {% for category, message in messages %}
                            <li style="color: {{ 'green' if category == 'success' else 'red' }};">{{ message }}</li>
                        {% endfor %}
                    </ul>
                {% endif %}
            {% endwith %}

            <form action="/cancella" method="POST">
                <label for="email">Inserisci la tua email:</label><br>
                <input type="email" id="email" name="email" required><br><br>
                <button type="submit">Cancella</button>
            </form>

            <p><a href="{{ url_for('index') }}">Torna alla pagina di prenotazione</a></p>
        </body>
        </html>
    ''')

// Avviamo l'applicazione
if __name__ == '__main__':
    init_db() // Inizializziamo il database
    app.run(debug=True)
