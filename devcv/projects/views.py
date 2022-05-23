from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import searchProjects, paginateProjects
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm


def projects(request):
    projects, search_query = searchProjects(request)
    custom_range, projects = paginateProjects(request, projects, 2)

    ctx = {'projects': projects,
           'search_query': search_query,
           'custom_range': custom_range}
    return render(request, 'projects/projects.html', ctx)


def project(request, pk):
    requested_project = Project.objects.get(id=pk)
    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        reviev = form.save(commit=False)
        reviev.project = requested_project
        reviev.owner = request.user.profile
        reviev.save()

        requested_project.getVoteCount

        messages.success(request, 'Your vote is added!')
        return redirect('project', pk=requested_project.id)

    ctx = {'project': requested_project, 'form': form}
    return render(request, 'projects/single-project.html', ctx)


@login_required(login_url='login')
def createProject(request):
    profile = request.user.profile
    form = ProjectForm()
    if request.method == "POST":
        newtags = request.POST.get('newtags').replace(',', " ").split()
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')

    ctx = {'form': form}
    return render(request, 'projects/project_form.html', ctx)


@login_required(login_url='login')
def updateProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)

    if request.method == "POST":
        newtags = request.POST.get('newtags').replace(',', " ").split()
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')

    ctx = {'form': form, 'project': project}
    return render(request, 'projects/project_form.html', ctx)


@login_required(login_url='login')
def deleteProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == "POST":
        project.delete()
        return redirect('projects')

    ctx = {'object': project}
    return render(request, 'delete_template.html', ctx)
