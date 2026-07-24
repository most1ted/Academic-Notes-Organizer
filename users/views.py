from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from users.forms import LoginForm, NoteForm
from django.http import HttpResponseRedirect, Http404,HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm,LoginForm,NoteForm,CourseForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Note,Course


@login_required
def accounts(request):
    return render(request,'accounts.html')
def log_out(request):
    logout(request)
    return redirect('login')

User = get_user_model()

class Login(AccessMixin, View):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('accounts')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        login_form = LoginForm()
        register_form = RegisterForm()

        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        if 'login_submit' in request.POST:
            login_form = LoginForm(request.POST)
            register_form = RegisterForm()

            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return HttpResponseRedirect(self.success_url)

            return render(request, self.template_name, {
                'login_form': login_form,
                'register_form': register_form
            })

        elif 'register_submit' in request.POST:
            register_form = RegisterForm(request.POST)
            login_form = LoginForm()

            if register_form.is_valid():
                username = register_form.cleaned_data['username']
                email = register_form.cleaned_data['email']
                password = register_form.cleaned_data['password']


                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                new_user.save()

                login(request, new_user)
                return redirect('accounts')



            return render(request, self.template_name, {
                'login_form': login_form,
                'register_form': register_form
            })

        return HttpResponseRedirect(self.success_url)
@login_required
def note_create(request,course_id):
    course = get_object_or_404(Course,id=course_id,user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST,request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.course = course
            note.user = request.user
            note.save()
            return redirect('notes',course_id=course_id)
    else:
        form = NoteForm()

    return render(request,'note.html',{
        'form':form,
    'course':course,
    })
@login_required
def note_edit(request,note_id):
    note = get_object_or_404(Note,id=note_id,user=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST,request.FILES)
        if form.is_valid():
            if 'file' in request.FILES:
                if note.file:
                    note.file.delete(save=False)
            note.save()
            return redirect('course',course_id=note.course.id)
        else:
            form = NoteForm(instance=note)
        return render(request,'note.html',{
        'form':form,
        'note':note,
    })
@login_required
def note_delete(request,note_id):
    note = get_object_or_404(Note,id=note_id,user=request.user)
    if not note.is_public and note.user != request.user:
        raise PermissionDenied("cant accses this file")
    if not note.file:
        raise Http404("there is no file")
    note.views_count += 1
    note.save()
    response = HttpResponse(note.file,content_type='application/octet-stream')
    response['Content-Length'] = f' file name="{note.original_filename}"'
    return response

def course_list(request):
    courses = Course.objects.all()
    return render(request,'course_list.html' ,{'courses':courses})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, 'Course created successfully')
            return redirect('courses')

        else:
            return render(request,'courses.html' ,{'form':form})
    form = CourseForm()
    return render(request,'courses.html',{'form':form})


@login_required
def course_edit(request,course_id):
    course = get_object_or_404(Course,id=course_id,user=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST,request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, 'Course created successfully')
            return redirect('courses',course_id=course.id)
        else:
            form = CourseForm(instance=course)
        return render(request,'course_form.html',{'form':form})
@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)

    if request.method == 'POST':
        course_title = course.title


        for note in course.notes.all():
            if note.file:
                note.file.delete(save=False)

        course.delete()
        messages.success(request, f'✅ Course "{course_title}" deleted successfully!')
        return redirect('courses')


    return render(request, 'course_delete.html', {'course': course})
def course_detail(request,course_id):
    course = get_object_or_404(Course,id=course_id,user=request.user)
    notes = course.notes.all()
    return render(request,'course_detail.html',{'course':course,'notes':notes})


@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).order_by('-created_at')
    search_query = request.GET.get('search', '')
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(summary__icontains=search_query)
        )

    course_filter = request.GET.get('course', '')
    if course_filter and course_filter.isdigit():
        notes = notes.filter(course_id=int(course_filter))


    courses = Course.objects.filter(user=request.user)


    total_notes = notes.count()
    public_notes = notes.filter(is_public=True).count()
    private_notes = notes.filter(is_public=False).count()
    notes_with_files = notes.exclude(file__isnull=True).count()

    context = {
        'notes': notes,
        'courses': courses,
        'search_query': search_query,
        'course_filter': course_filter,
        'total_notes': total_notes,
        'public_notes': public_notes,
        'private_notes': private_notes,
        'notes_with_files': notes_with_files,
    }

    return render(request, 'note_list.html', context)


@login_required
def note_download(request, note_id):

    note = get_object_or_404(Note, id=note_id)

    if not note.is_public and note.user != request.user:
        raise PermissionDenied("You don't have permission to download this file")

    if not note.file:
        raise Http404("No file attached to this note")

    note.views_count += 1
    note.save()

    response = HttpResponse(note.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{note.original_filename}"'
    return response

































