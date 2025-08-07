from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import difflib

app = Flask(__name__)

# Load and read the PDF file
reader = PdfReader("first_aid_guide.pdf")
pages = [p.extract_text() for p in reader.pages]

def search_pdf(query):
    query = query.lower()
    best_score = 0
    best_start = -1
    best_page_lines = []

    for page_text in pages:
        if not page_text:
            continue

        lines = page_text.strip().split('\n')
        for i, line in enumerate(lines):
            if line.isupper():
                score = difflib.SequenceMatcher(None, query, line.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_start = i
                    best_page_lines = lines

    if best_score > 0.4 and best_start != -1:
        section = []
        for i in range(best_start, len(best_page_lines)):
            line = best_page_lines[i].strip()
            if i != best_start and line.isupper() and len(line.split()) <= 5:
                break  # found next heading
            section.append(best_page_lines[i])
        return "\n".join(section)

    return None

# Sample database with friendly responses
disease_database = {
    "fever": "Viral fever is common. Rest, drink fluids, and take paracetamol.",
    "headache": "Can be caused by stress, dehydration, or screen time. Rest in a quiet place.",
    "cold": "Runny nose and sneezing? Rest and drink warm fluids.",
    "flu": "Body aches and high fever may be flu. Consider antiviral meds if severe.",
    "cough": "Dry or wet cough? Warm tea, honey, and rest help. See a doctor if it lasts.",
    "sore throat": "Try warm saltwater gargles. Avoid cold drinks.",
    "stomach pain": "Eat light food. Pain on the right side may be appendicitis.",
    "diarrhea": "Use ORS, avoid dairy/spicy food, and stay hydrated.",
    "vomiting": "Rest your stomach. Sip water. If continuous, seek help.",
    "rash": "May be allergy or infection. Use soothing cream, avoid itching.",
    "itching": "Skin allergies often cause itching. Try antihistamines if needed.",
    "acne": "Use mild cleansers. Avoid touching. See a dermatologist if severe.",
    "asthma": "Use inhaler if needed. Avoid dust and cold exposure.",
    "back pain": "Stretch gently. Heat therapy helps. Consult if it's sharp or chronic.",
    "dizziness": "May be low BP or ear issue. Sit down, drink water.",
    "ear pain": "May be infection. Avoid inserting anything inside the ear.",
    "eye redness": "Can be allergy or infection. Use cold compress and avoid rubbing.",
    "fatigue": "Can be from lack of sleep, anemia, or stress. Rest and eat healthy.",
    "gas": "Avoid fried foods. Walk after meals. Antacids can help.",
    "constipation": "Eat fiber, drink water, and stay active.",
    "nosebleed": "Sit upright, pinch nose bridge. Avoid tilting head back.",
    "nausea": "Can be motion sickness or food-related. Ginger tea helps.",
    "anxiety": "Practice deep breathing and mindfulness. Talk to someone.",
    "depression": "You’re not alone. Talk to a counselor. Stay active and connected.",
    "burn": "Run cold water, apply aloe vera. Don’t burst blisters.",
    "sprain": "Rest, Ice, Compress, Elevate (RICE method).",
    "fracture": "Immobilize and go to a hospital. Don’t move the bone.",
    "ulcer": "Avoid spicy food. Antacids or doctor-prescribed meds may help.",
    "high blood pressure": "Reduce salt, manage stress, and exercise regularly.",
    "low blood pressure": "Drink fluids, eat small meals. Sit down if dizzy.",
    "diabetes": "Eat balanced meals. Monitor sugar levels regularly.",
    "thyroid": "Tired, weight gain/loss? Get a thyroid test. Medicine can help.",
    "pcos": "Irregular periods, acne? Balanced diet and exercise help. See a doctor.",
    "period pain": "Use heating pad. Try gentle movement and pain relievers.",
    "chest pain": "Could be serious. If tightness or pain radiates — call emergency.",
    "palpitations": "Can be stress or heart-related. Calm yourself. Get checked.",
    "shortness of breath": "Rest and breathe slowly. Could be asthma, infection, or anxiety.",
    "covid": "Symptoms include cough, fever, and loss of smell. Isolate and monitor oxygen.",
    "measles": "High fever and red rash? Contagious — isolate and see a doctor.",
    "mumps": "Swelling near jaw? Avoid sour food and rest. See doctor.",
    "chickenpox": "Red itchy spots? Isolate and avoid scratching. Rest up.",
    "malaria": "Fever in waves, chills? Blood test needed. Use mosquito nets.",
    "dengue": "High fever, joint pain, red rash? Stay hydrated and get blood count.",
    "typhoid": "Long fever, stomach pain, and weakness. Needs antibiotics.",
    "hepatitis": "Yellow eyes? Liver inflammation. Avoid oily food. Do tests.",
    "jaundice": "Yellow skin or eyes? Rest, fluids, and no fatty foods.",
    "urine infection": "Burning urine? Drink water. Antibiotics might be needed.",
    "kidney stone": "Severe side pain? Drink water. Get ultrasound.",
    "appendicitis": "Sharp pain on lower right belly? Go to hospital quickly.",
    "migraine": "Throbbing headache with light sensitivity? Rest in a dark room.",
    "sinus": "Head feels heavy? Use steam and saline sprays.",
    "eczema": "Dry, itchy skin patches. Moisturize and avoid triggers.",
    "psoriasis": "Scaly skin? Not contagious. Needs dermatologist care.",
    "allergy": "Sneezing, rash, or itching? Antihistamines can help.",
    "heartburn": "Burning chest after eating? Avoid spicy food. Try antacids.",
    "tonsillitis": "Sore throat and swollen tonsils? Gargle and see doctor.",
    "bronchitis": "Cough with mucus? Rest, hydrate. May need antibiotics.",
    "pneumonia": "Chest pain, fever, cough? Needs X-ray and treatment.",
    "arthritis": "Joint pain and swelling? Gentle exercise and medication help.",
    "gout": "Sudden foot joint pain? Avoid meat and uric acid–rich food.",
    "insomnia": "Can't sleep? Avoid caffeine and screens. Try reading.",
    "obesity": "Eat smart, move daily, stay consistent. Small steps matter!",
    "underweight": "Eat more frequent meals, nuts, and protein-rich food.",
    "nose block": "Steam inhalation helps. Use nasal drops if prescribed.",
    "bleeding gums": "Brush gently. Vitamin C and dentist visit help.",
    "bad breath": "Brush tongue, floss, and drink water. Avoid onion/garlic.",
    "ear wax": "Don’t insert things inside! Use ear drops or see doctor.",
    "heat stroke": "Cool down fast. Drink ORS. Avoid going out in heat.",
    "sunburn": "Apply aloe vera. Stay in shade. Hydrate.",
    "acid reflux": "Eat slowly. Avoid lying down right after eating.",
    "snoring": "Change sleep position. Maintain healthy weight.",
    "hair fall": "Can be stress, diet, or genetics. Use mild shampoo. Eat protein.",
    "memory loss": "Forgetfulness? Try brain games and good sleep.",
    "lump": "Unusual lump? Monitor size. If painful or growing, get it checked.",
    "infection": "Redness, swelling, pain? Clean area and take prescribed meds.",
    "low oxygen": "Use oximeter. If below 92%, get help quickly.",
    "eye strain": "Follow 20-20-20 rule. Blink often and reduce screen time.",
    "dry eyes": "Use artificial tears and blink more.",
    "mouth ulcer": "Avoid spicy food. Rinse with salt water.",
    "dehydration": "Drink water, ORS. Dry mouth and dizziness are signs.",
    "food poisoning": "Vomiting, stomach pain after eating? Hydrate and rest.",
    "bloating": "Gas and full feeling? Walk around. Avoid fizzy drinks.",
    "hoarseness": "Rest your voice. Avoid shouting and drink warm water.",
    "hiccups": "Hold breath or drink cold water. Usually harmless.",
    "cramps": "Stretch gently. Stay hydrated.",
    "pregnancy symptoms": "Missed period, nausea, tiredness? Take a pregnancy test.",
    "UTI": "Burning when peeing? Drink water and see a doctor.",
    "insulin resistance": "Tired, weight gain? Get blood sugar test.",
    "liver pain": "Right upper belly pain? Get an ultrasound.",
    "gallstones": "Upper belly pain after eating fatty food? Get checked.",
    "pelvic pain": "Could be infection or cyst. Needs doctor check.",
    "infertility": "Many causes. Both partners should consult specialists.",
    "depression": "You're not alone. Get support, talk, walk, and never give up.",
    "panic attack": "Breathe slowly. You're safe. Talk to someone.",
    "choking": "Heimlich maneuver may be needed. Get emergency help."
}


greetings = ["hi", "hello", "hey", "salam", "assalamualaikum"]
goodbyes = ["bye", "goodbye", "thanks", "thank you"]

def get_response(msg):
    msg = msg.lower()

    if any(word in msg for word in greetings):
        return {"text": "Hello! I'm Dr. Nova. What symptoms are you experiencing today?"}
    
    if any(word in msg for word in goodbyes):
        return {"text": "You're welcome! Take care and get well soon."}

    for key in disease_database:
        if key in msg:
            return {"text": disease_database[key]}

    pdf_result = search_pdf(msg)
    if pdf_result:
        return {"text": pdf_result}

    return {"text": "I'm sorry, I didn't quite understand that. Can you describe your issue more clearly or try using simpler words?"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def respond():
    user_message = request.json.get("message")
    reply = get_response(user_message)
    return jsonify(reply)

if __name__ == "__main__":
    app.run(debug=True)
