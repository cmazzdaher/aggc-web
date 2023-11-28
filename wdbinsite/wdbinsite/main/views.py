"""Defines views for converting a Web requests into a Web responses"""

from django.shortcuts import render


def index(request):
    context = {"online": False}
    return render(request, 'home/index.html', context)