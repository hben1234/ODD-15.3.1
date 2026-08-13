# Dashboard — Dégradation des terres & Sécheresse (Maroc, SDG 15.3.1)

## Structure du projet

```text
dashboard_maroc/
├── app.py                     # Point d'entrée du dashboard Streamlit
├── src/
│   └── app.py                # Code principal de l'application
├── data/
│   ├── *.csv                 # Données analytiques
│   └── *.geojson             # Données géographiques
├── notebooks/
│   └── ...                   # Analyse exploratoire / prototypage
├── docs/
│   └── ...                   # Documentation et notes de projet
├── config/
│   └── ...                   # Fichiers de configuration
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## Lancement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Contenu

- **Synthèse exécutive** : KPIs, régions prioritaires, et signal sécheresse pour un briefing rapide
- **Carte régionale** : choroplèthe des 12 régions + classement
- **Dégradation** : statut détaillé, sous-indicateurs SDG 15.3.1 (productivité, couverture des sols, carbone)
- **Sécheresse** : exposition par région et évolution 2020–2024
- **Population** : population exposée, répartition hommes/femmes
- **Vulnérabilité (DVI)** : comparaison internationale + composantes (social, économique, infrastructurel)

## Personnalisation rapide

- Couleurs et style : dictionnaires `PALETTE` et `CUSTOM_CSS` dans le code principal de l'application
- Filtres (région, année) dans la barre latérale
- Première lecture : onglet « Synthèse exécutive » pour les décisions de comité
- Source des données : méthodologie Trends.Earth v2.2.6
