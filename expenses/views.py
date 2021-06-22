from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import json
import datetime
import csv
import xlwt

@login_required(login_url='/authentication/login')
def search_expenses(request):
    if request.method=='GET':
        search_str=json.loads(request.body).get(searchText)

        expenses= Expense.objects.filter(
        amount__istarts_with= search_str,
        owner=request.user,
        ) | Expense.objects.filter(
        date__istarts_with= search_str,
        owner=request.user,
        ) | Expense.objects.filter(
        category__icontains= search_str,
        owner=request.user,
        )

        data = expenses.values()

        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories= Category.objects.all()
    expenses= Expense.objects.filter(owner=request.user)

    paginator= Paginator(expenses,2)
    page_num= request.GET.get('page')
    page_obj= Paginator.get_page( paginator ,page_num)
    currency = UserPreference.objects.get(user=request.user).currency

    context={
        'expenses':expenses,
        'page_obj': page_obj,
        'currency': currency,

    }

    return render(request,'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def edit_expense(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)
        description = request.POST['description']
        date = request.POST['date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit_expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def delete_expense(request,id):
    expense= Expense.objects.get(pk=id)
    expense.delete()

    messages.info(request,'Removed')
    return redirect('expenses')



def expense_category_summary(request):
    todays_date= datetime.date.today()
    six_months_ago= todays_date-datetime.timedelta(days=30*6)
    expenses= Expense.objects.filter( owner=request.user,
    date__gte=six_months_ago, date__lte=todays_date
    )
    finalrep={}

    def get_category(expense):
        return expense.category

    category_list= list(set(map(get_category, expenses)))


    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    response= HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'

    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])

    expenses= Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])

    return response


def export_excel(request):
    response= HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'

    wb= xlwt.Workbook(encoding="utf-8")
    ws= wb.add_sheet('Expenses')
    row_num= 0
    font_style= xlwt.XFStyle()
    font_style.font.bold=True

    columns=['Amount','Description','Category','Date']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style= xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount','description','category','date')

    for row in rows:
        row_num +=1

        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)

    return response