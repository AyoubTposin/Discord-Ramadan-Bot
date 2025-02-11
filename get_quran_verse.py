import requests

def get_quran_verse():
    url = "https://api.quran.com/api/v4/verses/random?translations=131"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()

        verse = data.get("verse", {})
        if not verse:
            return "Invalid API response."

        translations = verse.get("translations", [])
        if not translations:
            return "No translation found."

        verse_text = translations[0].get("text", "No text available")
        verse_key = verse.get("verse_key", "Unknown Verse")  
        
        return f"**{verse_key}:**\n{verse_text}"
    else:
        return "Failed.Please try again later."