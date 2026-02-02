import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


# Initialisation du modèle Claude via LangChain
def get_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        temperature=0,
        max_tokens=100
    )


# Prompt pour la prédiction de note
RATING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Tu es un expert en analyse de sentiment pour les avis clients.
Analyse l'avis suivant et attribue une note de 1 à 5 étoiles.

Critères :
- 1 étoile : Très négatif, client très mécontent
- 2 étoiles : Négatif, client insatisfait
- 3 étoiles : Neutre ou mitigé
- 4 étoiles : Positif, client satisfait
- 5 étoiles : Très positif, client très satisfait

Réponds UNIQUEMENT avec un JSON de cette forme :
{{"rating": <note de 1 à 5>, "explanation": "<explication courte>"}}"""),
    ("human", "{review}")
])


@csrf_exempt
@require_http_methods(["POST"])
def predict_rating(request):
    """Prédit la note d'un avis client via Claude."""
    try:
        data = json.loads(request.body)
        review = data.get('review', '').strip()

        if not review:
            return JsonResponse({'error': 'Le champ "review" est requis'}, status=400)

        if not settings.ANTHROPIC_API_KEY:
            return JsonResponse({'error': 'ANTHROPIC_API_KEY non configurée'}, status=500)

        # Appel à Claude via LangChain
        llm = get_llm()
        chain = RATING_PROMPT | llm
        response = chain.invoke({"review": review})

        # Parser la réponse JSON
        try:
            result = json.loads(response.content)
            return JsonResponse({
                'rating': result.get('rating'),
                'explanation': result.get('explanation'),
                'review': review
            })
        except json.JSONDecodeError:
            # Si Claude ne retourne pas du JSON valide
            return JsonResponse({
                'rating': None,
                'explanation': response.content,
                'review': review,
                'error': 'Réponse non structurée'
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """Vérifie que l'API fonctionne."""
    return JsonResponse({
        'status': 'ok',
        'api_key_configured': bool(settings.ANTHROPIC_API_KEY)
    })
