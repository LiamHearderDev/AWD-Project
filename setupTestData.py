from app import db, create_app
from app.models import Paragraph, TypingResult
from app.config import ProductionConfig
import json
from app.config import ProductionConfig

application = create_app(ProductionConfig)

def add_paragraph(body, type=None): # add a new paragraph to the database

    # check to not add empty paragraph
    if not body or not body.strip():
        raise ValueError("Paragraph body cannot be empty")
    
    # check to see if paragraph has valid / recognisable characters
    allowed_characters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?-'")
    for character in body:
        if character not in allowed_characters:
            raise ValueError(f"Paragraph contains invalid character {character}")

    new_paragraph = Paragraph(body=body.strip(), type=type)
    db.session.add(new_paragraph)
    db.session.commit()
    return new_paragraph

test_phrases = [
    "Morning sunlight filters through pine trees, creating dancing shadows upon dew kissed grass and awakening sleepy birds with melodic cheerful songs.",
    "A gentle breeze carries fragrant petals across a shimmering lake while curious butterflies dance gracefully above water ripples at sunset.",
    "Thunder echoes in distant mountains as relentless rain pounds rocky pathways, inviting travelers to seek shelter near warm hearths and flickering candlelight.",
    "Night unfolds under silver moonlight, revealing celestial constellations that whisper ancient stories to wandering souls seeking inspiration beneath vast tranquil skies.",
    "Early explorers ventured beyond crooked horizons, charting unknown territories with steadfast courage and unyielding hope despite daunting challenges ahead on winding roads.",
    "Lively market stalls overflow with colorful fruits, fragrant spices, and handcrafted treasures while merchants skillfully weave tales to captivate passing curious wanderers.",
    "Silent snowfall blankets sleepy villages, muffling distant echoes and transforming familiar landscapes into pristine wonderlands that spark nostalgic warmth within weary hearts.",
    "Ancient ruins stand resolute against time's relentless march, bearing testament to forgotten civilizations and inspiring modern dreamers to explore history's hidden mysteries.",
    "Waves crash upon rugged shorelines, carving intricate sculptures of stone, as seagulls cry above turbulent surf under greying storm clouds gathering ominously overhead.",
    "Travelers gather around crackling fires at midnight, sharing whispered secrets and ancient legends beneath flickering starlight that illuminates hopeful faces aglow with wonder."
]

def add_many_paragraphs(test_paragraphs):
    for i in test_paragraphs:
        add_paragraph(i, 'normal')

if __name__ == "__main__":
    # push the Flask app context
    with application.app_context():
        add_many_paragraphs(test_phrases)
        print("Added test paragraphs")




