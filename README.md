# Analyse de Satisfaction Client - Supply Chain

Projet d'analyse de sentiment et de classification des avis clients pour la supply chain. Ce projet utilise des techniques de NLP (Natural Language Processing) et de Machine Learning pour prédire la satisfaction client à partir d'avis textuels.

## Structure du projet

```
PyCharmMiscProject/
├── README.md                   # Documentation du projet
├── requirements.txt            # Dépendances Python
│
├── config/
│   └── artefacts.json          # Métadonnées du pipeline (stopwords, params)
│
├── data/
│   ├── raw/
│   │   └── reviews_250825.csv  # Données brutes (avis scrappés)
│   └── processed/
│       ├── data.pkl            # Données sérialisées (stopwords, splits)
│       ├── reviews_clean.csv   # Avis nettoyés
│       ├── train.csv/.parquet  # Données d'entraînement
│       ├── val.csv/.parquet    # Données de validation
│       └── test.csv/.parquet   # Données de test
│
├── notebooks/
│   ├── 01_preprocessing.ipynb  # Nettoyage et préparation des données
│   ├── 02_dataViz.ipynb        # Visualisation et exploration
│   ├── 03_modelisation.ipynb   # Entraînement des modèles
│   ├── 04_clustering.ipynb     # Analyse par clustering (non supervisé)
│   └── archive/                # Anciens notebooks (référence)
│
├── models/
│   └── camembert/              # Checkpoints du modèle CamemBERT
│       ├── checkpoint-500/
│       ├── checkpoint-1000/
│       ├── checkpoint-1500/
│       └── checkpoint-1875/
│
└── outputs/
    ├── figures/                # Visualisations générées
    │   ├── pipeline_preprocessing.png
    │   └── pipeline_preprocessing.dot
    └── analysis/               # Résultats d'analyse
        └── top30_tokens_apres_nettoyage.csv
```

## Prérequis

### Système
- Python 3.9+
- Graphviz (pour la génération de diagrammes)

### Installation de Graphviz

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**Windows:**
Télécharger depuis https://graphviz.org/download/

### Installation des dépendances Python

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle spaCy français
python -m spacy download fr_core_news_sm
```

## Description des notebooks

### 01_preprocessing.ipynb - Prétraitement des données

**Objectif:** Transformer les avis bruts en un dataset propre et exploitable.

**Étapes:**
1. **Chargement et harmonisation** - Lecture du CSV, standardisation des colonnes
2. **Vérifications qualité** - Détection des NA, doublons exacts et approximatifs, filtrage par langue (FR)
3. **Split stratifié** - Séparation train/val/test (70/10/20) avec conservation des proportions de classes
4. **Nettoyage textuel:**
   - `text_dl` : nettoyage minimal (URLs, emails, n° commande supprimés) pour les modèles Deep Learning
   - `text_ml` : nettoyage agressif + lemmatisation + suppression stopwords pour TF-IDF
5. **Feature engineering** - Extraction de caractéristiques auxiliaires (longueur, ponctuation, majuscules, emojis)
6. **Sauvegarde** - Export en CSV/Parquet + artefacts JSON

**Outputs:**
- `data/processed/train.csv`, `val.csv`, `test.csv`
- `data/processed/data.pkl` (stopwords, données sérialisées)
- `config/artefacts.json`

---

### 02_dataViz.ipynb - Visualisation et exploration

**Objectif:** Explorer et comprendre la distribution des données.

**Analyses:**
1. **Distribution des notes** - Répartition des avis par note (1-5 étoiles)
2. **Analyse temporelle** - Évolution du volume d'avis dans le temps
3. **Longueur des avis** - Corrélation entre longueur et satisfaction
4. **WordClouds** - Nuages de mots globaux et par sentiment (positif/négatif)
5. **Top bigrammes** - Expressions les plus fréquentes
6. **Heatmaps** - Fréquence des termes/bigrammes par note
7. **Méta-features** - Distribution des exclamations, majuscules, emojis par note

**Insights clés:**
- Déséquilibre marqué : majorité d'avis 5 étoiles et 1 étoile
- Classes 2, 3, 4 sous-représentées
- Vocabulaire différencié entre avis positifs et négatifs

---

### 03_modelisation.ipynb - Entraînement des modèles

**Objectif:** Prédire la satisfaction client (classification 1-5 étoiles).

**Stratégies de rééquilibrage:**
- **Undersampling** - Réduction des classes majoritaires
- **Oversampling** - Duplication des classes minoritaires
- **SMOTE** - Génération d'exemples synthétiques (retenu automatiquement)

**Modèles évalués:**
1. **Baseline** - Prédiction de la classe majoritaire
2. **Régression Logistique + TF-IDF** - Modèle classique
3. **SVM** - Support Vector Machine
4. **Random Forest** - Ensemble d'arbres de décision
5. **LSTM** - Réseau de neurones récurrent
6. **CamemBERT** - Transformer pré-entraîné en français (fine-tuning)

**Métriques:**
- F1-macro (privilégié car dataset déséquilibré)
- Accuracy, Precision, Recall par classe
- Matrice de confusion

**Résultats attendus:**
- CamemBERT offre les meilleures performances, surtout sur les classes rares (2-3-4)
- Les modèles classiques ont tendance à prédire uniquement les classes majoritaires

---

### 04_clustering.ipynb - Analyse par clustering (non supervisé)

**Objectif:** Segmenter les avis clients en groupes homogènes sans utiliser les labels.

**Approches:**
1. **Clustering sur features non-textuelles** - Utilisation des méta-features (longueur, ponctuation, etc.)
2. **Clustering sur TF-IDF** - Vectorisation des textes puis KMeans
3. **Analyse temporelle** - Évolution des ratings dans le temps avec régression

**Techniques utilisées:**
- **KMeans** - Partitionnement en K clusters
- **Dendrogramme** - Clustering hiérarchique pour visualiser les proximités
- **WordCloud par cluster** - Mots caractéristiques de chaque groupe

**Visualisations:**
- Heatmap : répartition des ratings par cluster
- Échantillons d'avis par cluster
- Évolution temporelle avec moyenne glissante

**Cas d'usage:**
- Identifier des profils de clients (satisfaits fidèles, mécontents récurrents, etc.)
- Détecter des patterns non évidents dans les données
- Compléter l'analyse supervisée avec une vision non supervisée

---

## Comment exécuter le projet

### Étape 1 : Prétraitement
```bash
# Ouvrir et exécuter le notebook de preprocessing
jupyter notebook notebooks/01_preprocessing.ipynb
```
Exécuter toutes les cellules dans l'ordre. Cela génère les fichiers dans `data/processed/`.

### Étape 2 : Exploration (optionnel)
```bash
jupyter notebook notebooks/02_dataViz.ipynb
```
Visualiser les données pour comprendre leur distribution.

### Étape 3 : Modélisation
```bash
jupyter notebook notebooks/03_modelisation.ipynb
```
Entraîner et évaluer les différents modèles.

### Étape 4 : Clustering (optionnel)
```bash
jupyter notebook notebooks/04_clustering.ipynb
```
Analyse non supervisée pour segmenter les avis en clusters.

### Exécution rapide (sans Jupyter)
```bash
# Convertir et exécuter un notebook en script
jupyter nbconvert --to script notebooks/01_preprocessing.ipynb
python notebooks/01_preprocessing.py
```

## Données

### Format d'entrée (reviews_250825.csv)
| Colonne | Description |
|---------|-------------|
| review_text | Texte de l'avis client |
| rating | Note (1 à 5 étoiles) |
| title | Titre de l'avis |
| category | Catégorie du produit |
| datetime | Date de publication |
| product_slug | Identifiant du produit |

### Format de sortie (train/val/test.csv)
| Colonne | Description |
|---------|-------------|
| review_text | Texte brut |
| label | Note (1-5) |
| text_dl | Texte nettoyé pour Deep Learning |
| text_ml | Texte nettoyé pour ML classique |
| char_len | Longueur en caractères |
| word_count | Nombre de mots |
| exclam_count | Nombre de "!" |
| upper_ratio | Ratio de majuscules |
| flag_url/email/order | Indicateurs de présence |

## Modèles pré-entraînés

Les checkpoints CamemBERT sont stockés dans `models/camembert/`. Pour charger le meilleur modèle :

```python
from transformers import CamembertForSequenceClassification, CamembertTokenizer

model_path = "models/camembert/checkpoint-1875"
model = CamembertForSequenceClassification.from_pretrained(model_path)
tokenizer = CamembertTokenizer.from_pretrained(model_path)
```

## Auteurs

Projet réalisé dans le cadre d'une analyse de la satisfaction client pour la supply chain.
