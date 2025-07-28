# Prerequisites:
Install python3, pip3, venv

# Install:
First retrieve the project on your computer

```bash
git clone git@github.com:AdJez/ai_supply_chain.git
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
