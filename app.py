
from flask import Flask, render_template, request, abort
import requests

app = Flask(__name__)

API_BASE_URL = "https://my-json-server.typicode.com/BramS227/JSON-API-Webserver-Bram-S"

# Helper functie om data van de API te halen met foutafhandeling
def fetch_api_data(endpoint):
    try:
        # Stuur een GET-verzoek naar de opgegeven endpoint (met basis-URL ervoor)
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        response.raise_for_status()  # Dit zorgt ervoor dat we een foutmelding krijgen bij 4xx of 5xx statuscodes
        return response.json()  # Als de request succesvol was, retourneer de JSON-gegevens
    except requests.exceptions.RequestException as e:
        # Als er een fout is bij het ophalen van de data (bijvoorbeeld netwerkfout of fout van de API)
        print(f"Error fetching data from {endpoint}: {e}")
        return None  # Geef None terug als er een fout optreedt

# Route voor de homepage ('/')
@app.route('/')
def index():
    # Haal de lijst van motorfietsen op via de helperfunctie
    motorfietsen = fetch_api_data('motos')

    # Als de motorfietsen niet succesvol kunnen worden opgehaald (None wordt teruggegeven)
    if motorfietsen is None:
        # Geef een foutmelding door naar de template, zodat deze in de frontend kan worden getoond
        # We renderen de 'index.html' template met een foutmelding
        return render_template('index.html', error="Kon de motorfietsgegevens niet ophalen van de API.")

    # Render de 'index.html' template, geef de lijst van motorfietsen en een lege 'selected_motorfiets' mee
    # Dit is de standaardweergave van de lijst met motorfietsen
    return render_template('index.html', motorfietsen=motorfietsen, selected_motorfiets=None)

# Route voor de detailpagina van een specifieke motorfiets ('/motorfiets/<motorfiets_id>')
@app.route('/motorfiets/<int:motorfiets_id>')
def motorfiets_details(motorfiets_id):
    # Haal de gegevens van de specifieke motorfiets op via de helperfunctie
    motorfiets = fetch_api_data(f'motos/{motorfiets_id}')

    # Als de motorfiets niet gevonden is (bijvoorbeeld door een fout in de API of de motorfiets bestaat niet)
    if motorfiets is None:
        # Geef een 404-foutmelding als de motorfiets niet gevonden kan worden
        abort(404, description="Motorfiets niet gevonden of API-fout.")

    # Haal alle brandstofinformatie op via de helperfunctie
    all_brandstoffen = fetch_api_data('brandstoffen')

    # Als de brandstofinformatie niet succesvol opgehaald kan worden
    if all_brandstoffen is None:
        # Voeg een tekst toe aan de motorfiets die zegt dat de brandstofinformatie niet geladen kan worden
        motorfiets['brandstoffen_tekst'] = "Kon brandstofinformatie niet laden."
    else:
        # Filter de brandstoffen die bij deze motorfiets horen (op basis van motor_id)
        gevonden_brandstoffen = [
            f"{b['brandstof']} {b['soort']}"  # Combineer brandstof en soort als een enkele string
            for b in all_brandstoffen if b['motor_id'] == motorfiets['id']
        ]
        
        # Als er gevonden brandstoffen zijn, voeg ze toe aan de motorfiets
        if gevonden_brandstoffen:
            motorfiets['brandstoffen_tekst'] = ", ".join(gevonden_brandstoffen)
        else:
            # Als er geen brandstoffen gevonden zijn, geef een boodschap die aangeeft dat er geen brandstofinformatie beschikbaar is
            motorfiets['brandstoffen_tekst'] = "Geen specifieke brandstofinformatie beschikbaar."

    # Render de 'index.html' template met de geselecteerde motorfiets (details) en de brandstofinformatie
    return render_template('index.html', selected_motorfiets=motorfiets)

# Zorg ervoor dat de applicatie wordt uitgevoerd als het script direct wordt uitgevoerd
if __name__ == '__main__':
    app.run(debug=True)
