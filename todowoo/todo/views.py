from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required # decorator to check if the user is logged in
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from .forms import TodoForm
from .models import Todo

def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == "GET": # display the signup form
        return render(request, 'todo/signupuser.html', {"form": UserCreationForm()})
    else:
        # create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1'],
            )
                user.save()
                # login the user after signing up
                login(request, user) 
                return redirect('currenttodos')
            
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {"form": UserCreationForm(), "error": "Username already exists. Please choose another username."})
        else:
            return render(request, 'todo/signupuser.html', {"form": UserCreationForm(), "error": "Passwords do not match."})

@login_required
def currenttodos(request):
    # filter the todos by the current user, not completed, and order by date created descending
    todos = Todo.objects.filter(user=request.user, datecomplete__isnull=True).order_by('-created').all()
    return render(request, 'todo/currenttodos.html', {'todos': todos})

@login_required
def completedtodos(request):
    # filter the todos by the current user, completed, and order by date completed descending
    todos = Todo.objects.filter(user=request.user, datecomplete__isnull=False).order_by('-datecomplete').all()
    return render(request, 'todo/completedtodos.html', {'todos': todos})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user) # user=request.user is to make sure the todo belongs to the current user
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo) # recogize the existing object and update the todo
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad data passed in. Try again.'})

@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')

def loginuser(request):
    if request.method == "GET": # display the signup form
        return render(request, 'todo/loginuser.html', {"form": AuthenticationForm()})
    else:
        # login the user
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if user is None:
            return render(request, 'todo/loginuser.html', {"form": AuthenticationForm(), "error": "Username and password do not match."})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required        
def createtodo(request):
    if request.method == "GET":
        return render(request, 'todo/createtodo.html', {"form": TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user # add the current user to the todo
            newtodo.save() # save the todo to the database
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {"form": TodoForm(), "error": "Invalid data. Try again."})

@login_required 
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        # in currenttodos, only datecomplete is null items are displayed, 
        # updated datecomplete will make the todo filtered out
        todo.datecomplete = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required 
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')