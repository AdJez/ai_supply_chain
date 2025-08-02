# Prerequisites:
Install python3, pip3, venv

# Install:
First retrieve the project on your computer

```bash
git clone https://github.com/AdJez/ai_supply_chain.git
```

On your machine, create an env wherever you want. In this example we gonna place it the root of our machine.   

```python 
python3 -m venv ~/scrapy_env
```

Then activate your env

```python 
source ~/scrapy_env/bin/activate
```

Install dependencies included in requirements.txt

```pip3 install -r requirements.txt```

```pip3 freeze > requirements.txt```

Remember that ou can deactivate the env you are with the command ```deactivate``` at every needed moment.

# Architecture:

This project is made by two main parts. First part is.

# Crawl with Scrapy:

scrapy crawl trust

____________________________________________________________________________________________________________
Pour Windows: 

Étape 1 — Cloner le projet
```bash
git clone https://github.com/AdJez/ai_supply_chain.git
cd ai_supply_chain
```

 Étape 2 — Créer l’environnement virtuel
```bash
py -m venv venv
```

Étape 3 — Activer l’environnement virtuel
```powershell
.\venv\Scripts\Activate.ps1
```
ou
```bash
source venv/Scripts/activate
```
Si c'est bon, l'invite de commande va afficher: "(venv) PS C:\Users\...>"

Étape 4 — Installer les dépendances
```bash
pip install -r requirements.txt
```

Étape 5 — Vérifier que Scrapy fonctionne
```bash
scrapy list
```
Normalement ca affiche les spider dispo 

Étape 6 — Lancer un spider
```bash
scrapy crawl get_categories
```

Étape 7 — Désactiver l’environnement
```bash
deactivate
```


