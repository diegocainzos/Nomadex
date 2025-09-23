from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
import json
from .services.orquestrator import procesar_mensaje_usuario
from .models import Destinations


class HomePageView(TemplateView):
    template_name = "home.html"


class ChatPageView(TemplateView):
    template_name = "chatbot.html"


def chatbot_api(request):
    if request.method == "POST":
        # Supports HTMX form (request.POST) and JSON
        msg = request.POST.get("message")
        if msg is None:
            try:
                body = json.loads(request.body or "{}")
            except json.JSONDecodeError:
                body = {}
            msg = body.get("message", "")

        reply = procesar_mensaje_usuario(msg)
        print(reply, type(reply))

        # Regular JSON API
        return JsonResponse({"reply": str(reply)})
