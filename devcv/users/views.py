from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .utils import searchProfiles, paginateProfiles

from .forms import CustomUserCreationForm, PofileEditForm, SkillForm, MessageForm
from .models import Profile, Messages


def loginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'this user does not exist!')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'username or password is not correct!')

    return render(request, 'users/login_register.html')


def profiles(request):
    profiles, search_query = searchProfiles(request)

    custom_range, profiles = paginateProfiles(request, profiles, 3)

    ctx = {'profiles': profiles,
           'search_query': search_query,
           'custom_range': custom_range}
    return render(request, 'users/profiles.html', ctx)


def logoutUser(request):
    logout(request)
    messages.error(request, 'User was logged out!')
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'Your account has been created!')
            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'Error!')

    ctx = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', ctx)


def userProfie(request, pk):
    profile = Profile.objects.get(id=pk)

    top_skills = profile.skill_set.exclude(description__exact='')
    other_skills = profile.skill_set.filter(description='')
    ctx = {'profile': profile, 'top_skills': top_skills, 'other_skills': other_skills}
    return render(request, 'users/user-profile.html', ctx)


@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    ctx = {'profile': profile, 'skills': skills, 'projects': projects}
    return render(request, 'users/account.html', ctx)


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = PofileEditForm(instance=profile)

    if request.method == 'POST':
        form = PofileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')

    ctx = {'form': form}
    return render(request, 'users/profile_form.html', ctx)


@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill was added successfully!')
            return redirect('account')

    ctx = {'form': form}
    return render(request, 'users/skill_form.html', ctx)


@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill was added successfully!')
            return redirect('account')

    ctx = {'form': form}
    return render(request, 'users/skill_form.html', ctx)


@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill was deleted successfully!')
        return redirect('account')
    ctx = {'object': skill}
    return render(request, 'delete_template.html', ctx)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequest = profile.message.all()
    unreadMsgCount = messageRequest.filter(is_red=False).count()
    ctx = {'messageRequest': messageRequest, 'unreadMsgCount': unreadMsgCount}
    return render(request, 'users/inbox.html', ctx)


@login_required(login_url='login')
def viewMessage(request, pk):
    profile = request.user.profile
    userMessage = profile.message.get(id=pk)
    if userMessage.is_red == False:
        userMessage.is_red = True
        userMessage.save()
    ctx = {'userMessage': userMessage}
    return render(request, 'users/message.html', ctx)


def createMessage(request, pk):
    reveiver = Profile.objects.get(id=pk)
    form = MessageForm

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.receiver = reveiver

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, 'Your message has been sent!')
            return redirect('user-profile', pk=reveiver.id)
    ctx = {'reveiver': reveiver, 'form': form}
    return render(request, 'message_form.html', ctx)
