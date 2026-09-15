# Dashboard de dégradation des terres - Maroc

Application Streamlit consacrée au suivi de la dégradation des terres au Maroc selon l'indicateur **ODD 15.3.1** (neutralité en matière de dégradation des terres).

L'application présente les indicateurs disponibles par région, des analyses liées à la sécheresse et des cartes interactives fondées sur les données du projet.

## Fonctionnalités

- Synthèse régionale de l'indicateur ODD 15.3.1
- Analyse des sous-indicateurs et de l'évolution annuelle
- Analyse de la proportion de terres touchées par la sécheresse
- Indicateur de vulnérabilité DVI
- Cartes interactives MapLibre et couches Google Earth Engine lorsque la configuration GEE est disponible
- Visualisations, tableaux et exports proposés directement dans l'application

## Installation et lancement

### Prérequis

- Python 3.9 ou version ultérieure
- Un environnement virtuel Python recommandé
- Un projet Google Earth Engine pour les fonctionnalités qui utilisent les couches GEE

### Installation

```bash
git clone https://github.com/hben1234/ODD-15.3.1.git
cd ODD-15.3.1
python -m venv .venv
```

Sous PowerShell :

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Lancer l'application :

```bash
streamlit run app.py
```

L'application est ensuite accessible à l'adresse `http://localhost:8501`.

## Cartes interactives

Les cartes utilisent les sources définies dans `maplibre_sdg_sources.json` et les modules `live_map.py` et `live_map_sdg.py`. La disponibilité des couches Google Earth Engine dépend des URLs et des données accessibles au moment de l'exécution. Les données locales du dossier `data/` restent utilisées par l'application.

## Données et méthode

Le projet rassemble des données régionales marocaines pour :

- l'indicateur ODD 15.3.1 et ses sous-indicateurs ;
- la dégradation annuelle par région ;
- la proportion de terres touchées par la sécheresse ;
- la vulnérabilité DVI ;
- le statut régional et les géométries des 12 régions du Maroc.

Le notebook `notebook/SDG_15_3_1_UNCCD_GEE_Morocco_REPORT_final.ipynb` documente les traitements et l'analyse ayant servi à préparer les données du projet.

## Structure du projet

```text
ODD-15.3.1/
├── app.py                                      # Application Streamlit
├── live_map.py                                 # Carte interactive générale
├── live_map_sdg.py                             # Carte interactive ODD 15.3.1
├── maplibre_sdg_sources.json                   # Configuration des sources de carte
├── requirements.txt                            # Dépendances Python
├── .streamlit/config.toml                      # Configuration Streamlit
├── data/
│   ├── morocco_regions_12.geojson              # Géométries des régions
│   ├── provenance.json                          # Provenance des données
│   ├── sdg1531_degradation_by_region_annual.csv
│   ├── sdg1531_subindicators_by_region.csv
│   ├── so3_1_drought_land_proportion.csv
│   ├── so3_1_drought_land_proportion_2016_2025.csv
│   ├── so3_3_dvi_rebuilt.csv
│   ├── status_by_region.csv
│   └── status_expanded_by_region.csv
├── assets/                                     # Logos, icônes et images de l'application
└── notebook/
   └── SDG_15_3_1_UNCCD_GEE_Morocco_REPORT_final.ipynb
```

## Déploiement

Le dépôt contient le code nécessaire pour un déploiement Streamlit, mais aucune URL de production n'est actuellement déclarée. Un déploiement sur Streamlit Community Cloud est donc optionnel et pourra être configuré ultérieurement à partir de `app.py`, avec les secrets GEE définis dans les paramètres de l'application.

## Références

1. UNCCD (2021). *Good Practice Guidance for SDG Indicator 15.3.1*, version 2.
2. UNCCD (2021). *Good Practice Guidance for Strategic Objective 3*.
3. [Haut-Commissariat au Plan du Maroc - Développement durable et ODD](https://www.hcp.ma/Developpement-durable_r528.html).
