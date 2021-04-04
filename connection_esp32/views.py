from django.shortcuts import render


def index(request):
  return render(request, 'index.html', context={})

def connection(request):
  return render(request, 'base.html', context={'text': "Hello World"})