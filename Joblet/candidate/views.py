from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Candidate, Project, Education, Experince
from django.http import JsonResponse
from organization.models import Skill, Organization
from matchApp.models import OrganizationLike, CandidateLike, Match

# Create your views here.


@login_required
def candidate_profile_view(request, user_name):

    # if request.user.username != user_name:
    #
    #     messages.warning(request, 'There is error uploading your profile', 'alert-danger')
    #     return redirect('main:home_view')

    user = User.objects.get(username=user_name)
    candidate_profile = Candidate.objects.get(user=user.id)

    if request.method == 'POST':

        if 'about' in request.POST:
            candidate_profile.about = request.POST['about']

        if 'first_name' in request.POST:
            user.first_name = request.POST['first_name']

        if 'last_name' in request.POST:
            user.last_name = request.POST['last_name']

        if 'avatar' in request.FILES: candidate_profile.avatar = request.FILES['avatar']

        messages.success(request, 'profile updates successfully', 'alert-success')
        candidate_profile.save()

    return render(request, 'candidate/candidate_profile.html', {
        'candidate_profile': candidate_profile,
        'skills': Skill.objects.all(),
        'degree_choices': Education.DEGREE_CHOICES,

    })


def add_skill(request: HttpRequest):

    skill_id = request.POST['skill']
    skill = Skill.objects.get(pk=skill_id)
    candidate = Candidate.objects.get(user=request.user)
    candidate.skills.add(skill)
    if not candidate.profile_completion >= 100:
        candidate.profile_completion += 5
    candidate.save()
    messages.success(request, 'Skill was added Successfully', 'alert-success')
    return redirect('candidate:candidate_profile_view', user_name=request.user)


def remove_skill(request: HttpRequest, skill_id):
    try:
        skill = Skill.objects.get(pk=skill_id)
        candidate = Candidate.objects.get(user=request.user)
        candidate.skills.remove(skill)
        candidate.profile_completion -= 5
        candidate.save()
        messages.warning(request, 'Skill was removed Successfully', 'alert-warning')

    except Exception as e:

        print(e)
        messages.error(request, 'Error Deleting record', 'alert-danger')

    return redirect('candidate:candidate_profile_view', user_name=request.user)


def add_project(request: HttpRequest):

    with transaction.atomic():
        candidate = Candidate.objects.get(user=request.user)
        project = Project(
            profile = candidate,
            title = request.POST['title'],
            description = request.POST['description'],
            tools_used =request.POST['tools_used'],
        )
        project.save()

        if not candidate.profile_completion >= 100:
            candidate.profile_completion += 20

        candidate.save()

        messages.success(request, 'Project was added Successfully', 'alert-success')
    return redirect('candidate:candidate_profile_view', user_name=request.user)


def remove_project(request: HttpRequest, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        project.delete()

        candidate = Candidate.objects.get(user=request.user)
        candidate.profile_completion -= 20
        candidate.save()

        messages.warning(request, 'Project was removed Successfully', 'alert-warning')
    except Exception as e:
        print(e)
        messages.error(request, 'Error Deleting record', 'alert-danger')

    return redirect('candidate:candidate_profile_view', user_name=request.user)


def add_education(request: HttpRequest):

    with transaction.atomic():
        candidate = Candidate.objects.get(user=request.user)
        education = Education(
            profile=candidate,
            university=request.POST['university'],
            degree=request.POST['degree'],
            major=request.POST['major'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            GPA=float(request.POST['GPA']),
            certificate=request.POST['certificate']
        )

        # Save the education record
        education.save()

        if not candidate.profile_completion >= 100:
            candidate.profile_completion += 25

        candidate.save()

        messages.success(request, 'Project was added Successfully', 'alert-success')
    return redirect('candidate:candidate_profile_view', user_name=request.user)


def remove_education(request: HttpRequest, education_id):
    try:
        edu = Education.objects.get(pk=education_id)
        edu.delete()

        candidate = Candidate.objects.get(user=request.user)
        candidate.profile_completion -= 25
        candidate.save()

        messages.warning(request, 'Education was removed Successfully', 'alert-warning')

    except Experince as e:
        print(e)
        messages.error(request, 'Error Deleting record', 'alert-danger')

    return redirect('candidate:candidate_profile_view', user_name=request.user)


def add_experience(request: HttpRequest):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                candidate = Candidate.objects.get(user=request.user)
                experience = Experince(
                    profile=candidate,
                    company=request.POST['company'],
                    position=request.POST['position'],
                    start_date=request.POST['start_date'],
                    end_date=request.POST['end_date']
                )

                # Save the education record
                experience.save()

                if not candidate.profile_completion >= 100:
                    candidate.profile_completion += 25

                candidate.save()

            messages.success(request, 'Experience added successfully!', 'alert-success')
            return redirect('candidate:candidate_profile_view', user_name=request.user)
        except Experince as e:
            print(e)
            messages.error(request, 'Error adding Experience', 'alert-danger')

    return redirect('candidate:candidate_profile_view', user_name=request.user)


def remove_experience(request: HttpRequest, experience_id):
    try:
        exp = Experince.objects.get(pk=experience_id)
        exp.delete()

        candidate = Candidate.objects.get(user=request.user)
        candidate.profile_completion -= 25
        candidate.save()

        messages.warning(request, 'Education was removed Successfully', 'alert-warning')


    except Experince as e:
        print(e)
        messages.error(request, 'Error Deleting record', 'alert-danger')

    return redirect('candidate:candidate_profile_view', user_name=request.user)


def change_candidate_status(request: HttpRequest, candidate_id):
    candidate = Candidate.objects.get(pk=candidate_id)
    if request.user.is_superuser:
        candidate.approved = not candidate.approved
        candidate.save()
        messages.success(request, 'Candidate Status Updated successfully', 'alert-success')
    return redirect('dashboard:dashboard_view')



def check_and_create_match(organization, candidate):
    """
    Check if both OrganizationLike and CandidateLike exist, and create a Match if they do.
    """
    # Check if the organization likes the candidate
    org_liked_candidate = OrganizationLike.objects.filter(organization=organization, candidate=candidate).exists()
    # Check if the candidate likes the organization
    candidate_liked_org = CandidateLike.objects.filter(candidate=candidate, organization=organization).exists()
    # If both exist, create a Match if it doesn't already exist
    if org_liked_candidate and candidate_liked_org:
        match, created = Match.objects.get_or_create(organization=organization, candidate=candidate)
        if created:

            print("Match created!" , created)
            # request.session['new_match'] = True
            # request.session['match_org_name'] = organization.name  # Save org name for the popup

        else:
            print("Match already exists.")
        return match, created
    return None


def like_candidate(request, candidate_id):
    organization = Organization.objects.get(profile=request.user) # Assuming organization is tied to user
    candidate = Candidate.objects.get(id=candidate_id)

    try:
        org_like = OrganizationLike.objects.filter(organization=organization, candidate=candidate).first()
        # Add the like
        if org_like:
            messages.info(request, 'You have already liked this organization.', 'alert-info')
        else:
            OrganizationLike.objects.get_or_create(organization=organization, candidate=candidate)
        # Check for a match
            if check_and_create_match(organization, candidate):
                messages.success(request, f'Congrats there is a Match between you and {organization.name}', 'alert-dark')
            messages.success(request, 'Liked successfully!', 'alert-success')
    except Exception as e:
        print(e)
        messages.error(request, 'An error occurred while liking the organization.', 'alert-danger')

    return redirect(f'{reverse("main:home_view")}?type=organization&active={candidate_id}')
