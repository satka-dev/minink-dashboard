import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# CONFIGURATION
# ==========================================
# 1. Remplacez par l'URL de votre Web App Google Apps Script
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzWB_Vpb7CdvCrqTOB5vQ6-ZlY-Yvnqq4riN2nLj22-v7Q2hm0rlGgY9XRoeRB6dso/exec"

# 2. Dimensions de l'écran du Minink / X4 (Ajuster selon résolution exacte, ex: 480x800)
WIDTH = 480
HEIGHT = 800

def fetch_weather():
    """Récupère la météo actuelle à Toulouse via Open-Meteo API"""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.6047&longitude=1.4442&current_weather=true"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            temp = data['current_weather']['temperature']
            wind = data['current_weather']['windspeed']
            return f"Météo : {temp}°C (Vent: {wind} km/h)"
    except Exception as e:
        print(f"Erreur Météo: {e}")
    return "Météo indisponible"

def fetch_google_chart():
    """Télécharge le graphique depuis Google Apps Script"""
    try:
        # allow_redirects=True est vital pour suivre la redirection Google
        r = requests.get(GOOGLE_SCRIPT_URL, allow_redirects=True, timeout=15)
        if r.status_code == 200:
            image = Image.open(io.BytesIO(r.content))
            return image
    except Exception as e:
        print(f"Erreur Téléchargement Graphique: {e}")
    return None

def build_dashboard():
    # Création d'une image blanche en niveaux de gris (Mode 'L')
    img = Image.new('L', (WIDTH, HEIGHT), color=255)
    draw = ImageDraw.Draw(img)

    # Chargement d'une police par défaut
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 16)
    except:
        font_title = font_text = ImageFont.load_default()

    # --- ENTÊTE ---
    draw.text((20, 20), "TABLEAU DE BORD MININK", fill=0, font=font_title)
    draw.line([(20, 50), (WIDTH - 20, 50)], fill=0, width=2)

    # --- MÉTÉO ---
    weather_info = fetch_weather()
    draw.text((20, 65), weather_info, fill=0, font=font_text)

    # --- GRAPHIQUE ---
    chart_img = fetch_google_chart()
    if chart_img:
        # Redimensionnement du graphique pour rentrer proprement sur l'écran
        max_chart_width = WIDTH - 40
        w_percent = (max_chart_width / float(chart_img.size[0]))
        h_size = int((float(chart_img.size[1]) * float(w_percent)))
        
        chart_resized = chart_img.resize((max_chart_width, h_size), Image.Resampling.LANCZOS)
        
        # Superposition du graphique au milieu
        img.paste(chart_resized, (20, 110))

    # --- CONVERSION BMP 1-BIT OU 16 NIVEAUX DE GRIS ---
    # Conversion en noir & blanc tramé (1-bit Dithered) pour e-Ink natif
    bmp_final = img.convert('1')
    
    # Sauvegarde
    os.makedirs("dist", exist_ok=True)
    bmp_final.save("dist/sleep.bmp")
    print("Fichier dist/sleep.bmp généré avec succès !")

if __name__ == "__main__":
    build_dashboard()
