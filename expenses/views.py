import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from . import models
from .models import Category, Expense
from django.utils import timezone
from django.core.paginator import Paginator
from UserPreference.models import UserPreference


@login_required(login_url='authentication/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 8)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = "Not specified"
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
        # previous value
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    today = timezone.now()
    context = {
        'categories': categories,
        'values': request.POST,
        'today': today,
        # previous value
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not (amount and description and date):
            messages.error(request, 'You haven\'t finish all field,all is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(
            owner=request.user,
            amount=amount,
            description=description,
            date=date,
            category=category, )

        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


@login_required(login_url='authentication/login')
def edit_expense(request, id):
    categories = Category.objects.all()
    expense = Expense.objects.get(pk=id)

    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,

    }

    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        print(date)
        if not (amount and description and date):
            messages.error(request, 'You haven\'t finish all field,all is required')
            return render(request, 'expenses/add_expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.owner = request.user
        expense.category = category
        expense.description = description

        expense.save()

        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')


@login_required(login_url='authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')

    return redirect('expenses')


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(amount__istartswith=search_str, owner=request.user) \
                   | Expense.objects.filter(date__istartswith=search_str, owner=request.user) \
                   | Expense.objects.filter(description__icontains=search_str, owner=request.user) \
                   | Expense.objects.filter(category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
