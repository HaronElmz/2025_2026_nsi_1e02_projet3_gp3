{
  "start": "intro",
  "variables": {
    "has_key": False,
    "fear": 0,
    "trust_shadow": 0
  },
  "scenes": {
    "intro": {
      "background": "couloir.jpg",
      "music": "drone_01.mp3",
      "speaker": "narrateur",
      "text": "Tu te réveilles dans une maison que tu ne reconnais pas.",
      "choices": [
        {
          "text": "Explorer le salon",
          "next": "salon"
        },
        {
          "text": "Monter à l'étage",
          "next": "etage",
          "effects": {
            "fear": 1
          }
        }
      ]
    },
    "salon": {
      "speaker": "narrateur",
      "text": "Sur la table, une clé rouillée repose à côté d'une photo déchirée.",
      "choices": [
        {
          "text": "Prendre la clé",
          "next": "salon_cle",
          "effects": {
            "has_key": True
          }
        },
        {
          "text": "Ignorer la clé",
          "next": "photo"
        }
      ]
    },
    "etage": {
      "speaker": "narrateur",
      "text": "Une porte fermée bloque le couloir.",
      "choices": [
        {
          "text": "Utiliser la clé",
          "next": "chambre",
          "conditions": {
            "has_key": True
          }
        },
        {
          "text": "Forcer la porte",
          "next": "mort_brulee"
        }
      ]
    }
  }
}