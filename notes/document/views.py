from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError

@login_required(login_url='/login/')
def editor(request):
    docid = int(request.GET.get('docid', 0))
    notes = Note.objects.all()

    if request.method == 'POST':
        return handle_note_post(request)

    note = get_object_or_404(Note, pk=docid) if docid > 0 else None

    context = {
        'docid': docid,
        'notes': notes,
        'note': note
    }

    return render(request, 'editor.html', context)

@login_required(login_url='/login/')
def delete_note(request, docid):
    note = get_object_or_404(Note, pk=docid)
    note.delete()
    messages.success(request, "Note deleted successfully.")
    return redirect(f"{reverse('editor')}?docid=0")

def login_page(request):
    if request.method == "POST":
        return handle_login_post(request)
    return render(request, 'login.html')

def register_page(request):
    if request.method == "POST":
        return handle_register_post(request)
    return render(request, 'register.html')

@login_required(login_url='/login/')
def custom_logout(request):
    logout(request)
    return redirect('login')

def handle_note_post(request):
    docid = int(request.POST.get('docid', 0))
    title = request.POST.get('title')
    content = request.POST.get('content', '')

    if docid > 0:
        note = get_object_or_404(Note, pk=docid)
        note.title = title
        note.content = content
        note.save()
        messages.success(request, "Note updated successfully.")
    else:
        note = Note.objects.create(title=title, content=content)
        messages.success(request, "Note created successfully.")
    
    return redirect(f"{reverse('editor')}?docid={note.id}")

def handle_login_post(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('editor')
    else:
        messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def handle_register_post(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    try:
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect(reverse('login'))
    except IntegrityError:
        messages.error(request, "Username is already taken.")
    return render(request, 'register.html')
