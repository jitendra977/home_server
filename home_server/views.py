from django.shortcuts import render

def dashboard(request):
    return render(request, 'pages/dashboard.html')  
def charts(request):
    return render(request, 'pages/charts/chartjs.html')  
def forms(request):
    return render(request, 'pages/forms/basic_elements.html')  
def icons(request):
    return render(request, 'pages/icons/mdi.html')  
def login(request):
    return render(request, 'pages/samples/login.html')
def register(request):
    return render(request, 'pages/samples/register.html')
def tables(request):
    return render(request, 'pages/tables/basic-table.html')    