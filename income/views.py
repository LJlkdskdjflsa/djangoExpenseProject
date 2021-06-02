import json
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import models
from .models import Source, Income
from django.utils import timezone
from django.core.paginator import Paginator
from UserPreference.models import UserPreference


@login_required(login_url='authentication/login')
def index(request):
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': incomes,
        'page_obj': page_obj,
        'currency' : currency
        # previous value
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='authentication/login')
def add_income(request):
    sources = Source.objects.all()
    today = timezone.now()
    context = {
        'sources': sources,
        'values': request.POST,
        'today': today,
        # previous value
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not (amount and description and date):
            messages.error(request, 'You haven\'t finish all field,all is required')
            return render(request, 'income/add_income.html', context)

        Income.objects.create(
            owner=request.user,
            amount=amount,
            description=description,
            date=date,
            source=source, )

        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='authentication/login')
def edit_income(request, id):
    categories = Source.objects.all()
    income = Income.objects.get(pk=id)

    context = {
        'income': income,
        'values': income,
        'categories': categories,

    }

    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        print(date)
        if not (amount and description and date):
            messages.error(request, 'You haven\'t finish all field,all is required')
            return render(request, 'income/add_income.html', context)

        income.owner = request.user
        income.amount = amount
        income.owner = request.user
        income.source = source
        income.description = description

        income.save()

        messages.success(request, 'Income saved successfully')

        return redirect('income')


@login_required(login_url='authentication/login')
def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Record removed')

    return redirect('income')


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        incomes = Income.objects.filter(amount__istartswith=search_str, owner=request.user) \
                   | Income.objects.filter(date__istartswith=search_str, owner=request.user) \
                   | Income.objects.filter(description__icontains=search_str, owner=request.user) \
                   | Income.objects.filter(source__icontains=search_str, owner=request.user)
        data = incomes.values()
        return JsonResponse(list(data), safe=False)