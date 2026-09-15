# Dashboard Dégradation des Terres - Maroc

Dashboard interactif pour le suivi de la dégradation des terres au Maroc selon l'indicateur **ODD 15.3.1** (Neutralité en matière de dégradation des terres).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## Fonctionnalités

### **Cartographie Interactive**
- Visualisation régionale de la dégradation des terres
- Cartes live avec tuiles Google Earth Engine (NRT)
- Couches SDG 15.3.1 officielles et alertes quasi temps réel

### **Analyses Multi-Indicateurs**
- **SDG 15.3.1**: Productivité, Couverture des terres, Carbone organique du sol
- **Sécheresse SO3-1**: Indice de précipitations standardisé (SPI-12)
- **Vulnérabilité DVI**: Comparaison régionale (pays voisins)

### **Recommandations Stratégiques**
- Priorisation territoriale dynamique
- Plans d'action régionalisés
- Mesures d'adaptation au changement climatique
- Budget estimatif et parties prenantes

### **Interface Professionnelle**
- Branding HCP (Haut-Commissariat au Plan)
- Design responsive et accessible
- Export CSV de toutes les analyses
- Navigation par onglets intuitive

---

## Démo Live

**URL de production**: [https://votre-app.streamlit.app](https://votre-app.streamlit.app) *(à configurer)*

---

## Installation Locale

### Prérequis
- Python 3.9+
- Compte Google Earth Engine (optionnel, pour cartes live)

### Installation

```bash
# Cloner le repository
git clone https://github.com/VOTRE-USERNAME/dashboard-maroc.git
cd dashboard-maroc

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditez .env avec vos identifiants GEE

# Lancer l'application
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

---

## Structure du Projet

```
dashboard-maroc/
├── app.py                          # Application principale
├── requirements.txt                # Dépendances Python
├── .streamlit/
│   └── config.toml                # Configuration Streamlit
├── data/
│   ├── status_by_region.csv       # Statut SDG par région
│   ├── drought_*.csv              # Données sécheresse
│   ├── dvi_*.csv                  # Vulnérabilité sécheresse
│   └── morocco_regions_12.geojson # Géométries régions
├── assets/
│   ├── hcp_logo.jpg               # Logo HCP
│   ├── flag.png                   # Drapeau Maroc
│   └── drought.png                # Icône sécheresse
├── live_map.py                    # Module carte MapLibre
├── refresh_sdg_tiles.py           # Script rafraîchissement tuiles SDG
├── refresh_gee_tiles.py           # Script rafraîchissement tuiles NRT
└── DEPLOIEMENT_STREAMLIT_CLOUD.md # Guide de déploiement
```

---

## Méthodologie

### Données Sources
- **SDG 15.3.1**: Trends.Earth v2.2.6, UNCCD GPG v2 (2021) + Addendum 2025
- **Période de référence**: 2001-2015
- **Période de suivi**: 2016-2025
- **Sécheresse**: CHIRPS, SPI-12 empirique
- **Géométries**: Régions administratives du Maroc (12 régions)

### Sous-Indicateurs SDG 15.3.1
1. **Productivité des terres** (MODIS NPP, Trends in LPD)
2. **Couverture des terres** (MODIS MCD12Q1)
3. **Carbone organique du sol** (OpenLandMap)

### Catégorisation
- **Dégradé**: Déclin dans ≥1 indicateur sans amélioration
- **Stable**: Pas de changement significatif
- **Amélioré**: Amélioration dans ≥1 indicateur sans déclin

---

## Configuration Avancée

### Authentification Google Earth Engine

Pour utiliser les cartes live, vous devez:

1. **Créer un projet GEE**: https://code.earthengine.google.com/
2. **Exporter vos assets** depuis le notebook Colab fourni
3. **Configurer les secrets**:
   - Localement: fichier `.env`
   - Streamlit Cloud: Settings → Secrets

```toml
# Dans Streamlit Cloud > Settings > Secrets
GEE_PROJECT_ID = "ee-votreusername"
GEE_ASSET_ROOT = "projects/ee-votreusername/assets/ldn"
```

### Rafraîchissement des Tuiles

Les URLs de tuiles GEE expirent après quelques heures. Pour les rafraîchir:

```bash
# Régénérer les tuiles SDG 15.3.1
python refresh_sdg_tiles.py

# Régénérer les tuiles NRT (Near Real-Time)
python refresh_gee_tiles.py
```

Les fichiers JSON générés (`maplibre_*_sources.json`) doivent être committés sur GitHub.

---

## Déploiement sur Streamlit Community Cloud

Suivez le guide détaillé: [DEPLOIEMENT_STREAMLIT_CLOUD.md](DEPLOIEMENT_STREAMLIT_CLOUD.md)

**Résumé rapide:**

1. Poussez votre code sur GitHub
2. Connectez-vous sur https://share.streamlit.io/
3. Sélectionnez votre repository
4. Configurez les secrets GEE
5. Déployez!

---

## Captures d'Écran

### Synthèse Exécutive
![Synthèse](https://via.placeholder.com/800x400?text=Synthese+Executive)

### Carte Régionale
![Carte](https://via.placeholder.com/800x400?text=Carte+Regionale)

### Recommandations
![Recommandations](https://via.placeholder.com/800x400?text=Recommandations+Strategiques)

---

## Contribution

Les contributions sont les bienvenues! 

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Poussez sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## TODO / Roadmap

- [ ] **Automatisation**: Pipeline GitHub Actions pour rafraîchir les tuiles quotidiennement
- [ ] **Export PDF**: Générer un rapport PDF des recommandations
- [ ] **Comparaison Temporelle**: Visualiser l'évolution entre périodes de reporting
- [ ] **API REST**: Exposer les données via API pour intégration externe
- [ ] **Multilangue**: Ajouter support Arabe/Anglais
- [ ] **Mobile**: Optimiser l'interface pour smartphones
- [ ] **Cache Redis**: Accélérer le chargement avec cache distribué

---

## Licence

© 2024 Haut-Commissariat au Plan (HCP) - Royaume du Maroc

Ce projet est développé dans le cadre du suivi des Objectifs de Développement Durable (ODD) au Maroc.

---

## Contact

**Haut-Commissariat au Plan (HCP)**
- Site web: https://www.hcp.ma
- Email: contact@hcp.ma

**Développeur**
- GitHub: [@VOTRE-USERNAME](https://github.com/VOTRE-USERNAME)

---

## Remerciements

- **UNCCD**: Convention des Nations Unies sur la lutte contre la désertification
- **Trends.Earth**: Conservation International
- **Google Earth Engine**: Google
- **Streamlit**: Snowflake Inc.
- **OpenLandMap**: EnvirometriX

---

## Références

1. UNCCD (2021). *Good Practice Guidance for SDG Indicator 15.3.1 (version 2)*
2. UNCCD (2021). *Good Practice Guidance for Strategic Objective 3*
3. Trends.Earth (2024). *User Guide v2.2.6*
4. HCP (2023). *Plan National de Lutte contre la Désertification (PAN-LCD)*
5. Ministère de l'Agriculture (2020). *Stratégie Génération Green 2020-2030*

---

**Construit pour le développement durable du Maroc**
