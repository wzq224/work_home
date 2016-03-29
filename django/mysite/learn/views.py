#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse


# def index(request):
#     return HttpResponse(u"傻逼")

def add(request):
    a = request.GET['a']
    b = request.GET['b']
    c = int(a)+int(b)
    return HttpResponse(str(c))

def add2(request,a,b):
    c = int(a)+int(b)
    return HttpResponse(str(c))

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

def show_add_form(request):
    return render(request, 'add_form.html')