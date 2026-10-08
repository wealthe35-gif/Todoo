# Create your views here.
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from .models import Todo

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Grab the authenticated user from the form
            user = form.get_user()
            # Log them in (drops the session cookie/wristband)
            login(request, user)
            return redirect('todo_list')
    else:
        form = AuthenticationForm()
    
    return render(request, 'todo/login.html', {'form': form})

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('todo_list')
    else:
        form = UserCreationForm()

    return render(request, 'todo/signup.html', {'form': form})

@login_required(login_url='login')
def todo_list(request):
    todos = Todo.objects.filter(owner=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            Todo.objects.create(title=title, owner=request.user)
        return redirect('todo_list')
        
    return render(request, 'todo/todo.html', {'todos': todos})
@login_required(login_url='login')
@require_POST
def update_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo_list')

@login_required(login_url='login')
@require_POST
def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.delete()
    return redirect('todo_list')
