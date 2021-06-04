from django.shortcuts import render

@login_required(login_url='authentication/login')
def expenses_category_summary(request):
    today = datetime.date.today()
    sixmonth_ago = today - datetime.timedelta(3*60)
    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=sixmonth_ago,
        date__lte=today,
    )

    #helper function
    def get_category(expense):
        return expense.category

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount

        return amount

    category_list = list(set(map(get_category, expenses)))
    final_representation = {}

    for expense in expenses:
        for category in category_list:
            final_representation[category] = get_expense_category_amount[category]

    return JsonResponse({'expense_category_data': final_representation}, safe=False)
