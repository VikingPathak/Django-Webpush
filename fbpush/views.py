#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import json
import os
import sys

from django.conf import settings
from django.shortcuts import render
from django.http import request, HttpResponse, JsonResponse
from pywebpush import webpush
from django.views.decorators.http import require_http_methods, require_POST, require_GET

VAPID_CLAIMS = {
    "sub": "mailto:apathak092@gmail.com"
}


@require_GET
def send_web_push(subscription_information, message_body):
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    private_key = webpush_settings.get('VAPID_PRIVATE_KEY')
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=private_key,
        vapid_claims=VAPID_CLAIMS
    )

@require_GET
def index(request):
    return render(request, 'index.html')


@require_http_methods(["GET", "POST"])
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    public_key = webpush_settings.get('VAPID_PUBLIC_KEY')

    if request.method == "GET":
        return HttpResponse(response=json.dumps({"public_key": public_key}),
                            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")

    subscription_token = request.get_json("subscription_token")
    return HttpResponse(status=201, mimetype="application/json")


@require_POST
def push_v1():
    message = "Push Test v1"
    print("is_json", request.is_json)

    if not request.json or not request.json.get('sub_token'):
        return JsonResponse({'failed': 1})

    print("request.json", request.json)

    token = request.json.get('sub_token')
    try:
        token = json.loads(token)
        send_web_push(token, message)
        return JsonResponse({'success': 1})

    except Exception as e:
        print("error", e)
        return JsonResponse({'failed': str(e)})
