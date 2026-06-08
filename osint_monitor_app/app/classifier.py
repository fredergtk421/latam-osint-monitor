import hashlib
import re
from typing import Tuple

EVENT_KEYWORDS = {
    "protest": ["protesta", "manifestación", "marcha", "paro", "huelga", "cacerolazo", "demonstration", "strike", "protest"],
    "roadblock": ["bloqueo", "corte de ruta", "piquete", "carretera bloqueada", "roadblock", "blockade", "blocked highway"],
    "violence": ["disturbios", "enfrentamiento", "tiroteo", "ataque", "heridos", "muertos", "violencia", "riot", "clashes", "shooting", "attack"],
    "organized_crime": ["narcotráfico", "cartel", "sicarios", "crimen organizado", "extorsión", "secuestro", "drug cartel", "kidnapping"],
    "cyber": ["ciberataque", "ransomware", "hackeo", "brecha de datos", "cyberattack", "data breach", "hacked"],
    "election": ["elección", "elecciones", "votación", "comicios", "ballot", "election"],
    "natural_disaster": ["sismo", "terremoto", "inundación", "huracán", "incendio forestal", "volcán", "earthquake", "flood", "hurricane", "wildfire"],
    "infrastructure": ["apagón", "explosión", "oleoducto", "gasoducto", "puerto", "mina", "refinería", "power outage", "pipeline", "port", "mine"],
    "logistics": ["frontera", "aduana", "camioneros", "transporte", "puerto", "aeropuerto", "supply chain", "logistics", "border"],
    "corporate_security": ["empresa", "empleados", "expatriado", "planta", "instalación", "corporate", "facility", "workers"],
}

SEVERITY_TERMS = {
    "critical": ["golpe de estado", "estado de sitio", "secuestro", "ataque a mina", "muertos", "masacre", "coup", "kidnapping", "massacre"],
    "high": ["bloqueo", "disturbios", "huelga nacional", "ataque", "incendio", "frontera cerrada", "roadblock", "riot", "attack", "closed border"],
    "medium": ["protesta", "paro", "manifestación", "apagón", "demora", "strike", "protest", "outage", "delay"],
}

COUNTRY_TERMS = {
    "Argentina": ["argentina", "buenos aires", "rosario", "mendoza"],
    "Brazil": ["brasil", "brazil", "rio de janeiro", "são paulo", "sao paulo"],
    "Chile": ["chile", "santiago", "valparaíso", "valparaiso"],
    "Colombia": ["colombia", "bogotá", "bogota", "medellín", "medellin", "cali"],
    "Ecuador": ["ecuador", "quito", "guayaquil"],
    "Mexico": ["méxico", "mexico", "cdmx", "ciudad de méxico", "monterrey", "jalisco"],
    "Peru": ["perú", "peru", "lima", "callao", "arequipa"],
    "Uruguay": ["uruguay", "montevideo"],
    "Venezuela": ["venezuela", "caracas", "maracaibo"],
    "Bolivia": ["bolivia", "la paz", "santa cruz"],
    "Paraguay": ["paraguay", "asunción", "asuncion"],
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def classify_event(text: str) -> str:
    t = normalize_text(text)
    best_type = "other"
    best_hits = 0
    for event_type, terms in EVENT_KEYWORDS.items():
        hits = sum(1 for term in terms if term in t)
        if hits > best_hits:
            best_type = event_type
            best_hits = hits
    return best_type


def score_severity(text: str, event_type: str) -> Tuple[str, int]:
    t = normalize_text(text)
    for level in ["critical", "high", "medium"]:
        if any(term in t for term in SEVERITY_TERMS[level]):
            return level, {"critical": 95, "high": 75, "medium": 50}[level]
    if event_type in ["violence", "organized_crime", "infrastructure"]:
        return "high", 70
    if event_type in ["roadblock", "logistics", "cyber", "natural_disaster"]:
        return "medium", 55
    return "low", 25


def infer_country(text: str, fallback: str = "Unknown") -> str:
    t = normalize_text(text)
    for country, terms in COUNTRY_TERMS.items():
        if any(term in t for term in terms):
            return country
    return fallback or "Unknown"


def confidence_from_source(source_type: str, text: str) -> str:
    t = normalize_text(text)
    if source_type == "gdelt":
        return "medium"
    if len(t) > 400:
        return "medium"
    return "low"


def build_dedupe_key(title: str, country: str, event_type: str) -> str:
    cleaned = normalize_text(title)
    words = [w for w in re.findall(r"[a-záéíóúñü0-9]+", cleaned) if len(w) > 3]
    core = " ".join(words[:10])
    raw = f"{country}|{event_type}|{core}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def enrich_event_dict(event: dict) -> dict:
    text = " ".join([event.get("title", ""), event.get("summary", ""), event.get("raw_text", "")])
    event_type = classify_event(text)
    severity, score = score_severity(text, event_type)
    country = infer_country(text, event.get("country", "Unknown"))
    confidence = confidence_from_source(event.get("source_type", "unknown"), text)
    event.update({
        "event_type": event_type,
        "severity": severity,
        "confidence": confidence,
        "score": score,
        "country": country,
        "dedupe_key": build_dedupe_key(event.get("title", ""), country, event_type),
    })
    return event


def analyst_alert(row: dict) -> str:
    title = row.get("title", "Untitled")
    country = row.get("country", "Unknown")
    event_type = row.get("event_type", "other")
    severity = row.get("severity", "low").upper()
    confidence = row.get("confidence", "low")
    summary = row.get("summary", "") or row.get("raw_text", "")[:300]
    url = row.get("url", "")
    impact = "Potential business/security relevance. Analyst review recommended."
    if event_type in ["roadblock", "logistics", "infrastructure"]:
        impact = "Potential disruption to logistics, transport routes, ports, mines, energy assets or local operations."
    elif event_type in ["violence", "organized_crime"]:
        impact = "Potential threat to personnel, travel, facilities and third-party operations."
    elif event_type == "protest":
        impact = "Potential disruption to movement, public order and government/business activity."

    return f"""{severity} | {country} | {event_type}\n\n{title}\n\nWhat happened:\n{summary}\n\nWhy it matters:\n{impact}\n\nConfidence: {confidence}\nSource: {url}\n"""
