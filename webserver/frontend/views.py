from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def node_index(request:HttpRequest) -> HttpResponse:
    return render(request, 'index.html')

def node_hello(request:HttpRequest) -> HttpResponse:
    return HttpResponse('Hello!')
