import spacy
import json

def build_skill_extractor(taxonomy_path="ml/skills_taxonomy.json"):
    with open(taxonomy_path) as f:
        taxonomy = json.load(f)

    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")

    patterns = []
    for category, skills in taxonomy.items():
        for skill in skills:
            patterns.append({"label": "SKILL", "pattern": skill})
            # also match case-insensitively, token by token
            patterns.append({
                "label": "SKILL",
                "pattern": [{"LOWER": w.lower()} for w in skill.split()]
            })

    ruler.add_patterns(patterns)
    return nlp

def extract_skills(nlp, text):
    if not text:
        return []
    doc = nlp(text)
    return sorted(set(ent.text for ent in doc.ents if ent.label_ == "SKILL"))