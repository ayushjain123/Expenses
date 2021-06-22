from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='income'),
    path('add-income', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.edit_income, name='edit-income'),
    path('delete-income/<int:id>', views.delete_income, name='delete-income'),
    path('search-income/<int:id>', views.search_income, name='seach-income'),
    path('income_source_summary', views.income_source_summary, name='income_source_summary'),
    path('stats', views.stats, name='income-stats'),
    path('export_excel', views.export_excel, name='export-excel'),
    path('export_csv', views.export_csv, name='export-csv'),

]
