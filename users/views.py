from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth import  login, logout
from .forms import RegisterForm,LoginForm,CourseForm
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import  HttpResponse
from django.db.models import Q
from .forms import NoteForm
from .models import Note, Course, User, NoteFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def accounts(request):
    return render(request, 'accounts/accounts.html')
def log_out(request):
    logout(request)
    return redirect('login')

User = get_user_model()

class Login(AccessMixin, View):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('main')

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
                return redirect('main')



            return render(request, self.template_name, {
                'login_form': login_form,
                'register_form': register_form
            })

        return HttpResponseRedirect(self.success_url)




@login_required
def note_delete(request, note_id):

    note = get_object_or_404(Note, id=note_id, user=request.user)
    course_id = note.course.id

    if request.method == 'POST':
        try:
            note_title = note.title


            if hasattr(note, 'files') and note.files.exists():
                for file_obj in note.files.all():
                    if file_obj.file:
                        try:
                            file_obj.file.delete(save=False)
                        except Exception as e:
                            print(f"Error deleting file: {e}")
                    file_obj.delete()


            note.delete()
            messages.success(request, f' Note "{note_title}" deleted successfully!')

        except Exception as e:
            messages.error(request, f' Error deleting note: {str(e)}')

        return redirect('course_detail', course_id=course_id)

    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
def course_list(request):



    my_courses = Course.objects.filter(user=request.user).order_by('-created_at')


    all_courses = Course.objects.filter(
        is_public=True
    ).exclude(
        user=request.user
    ).order_by('-created_at')


    search_query = request.GET.get('search', '').strip()
    if search_query:
        my_courses = my_courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(code__icontains=search_query)
        )
        all_courses = all_courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(code__icontains=search_query)
        )


    status_filter = request.GET.get('status', '')
    if status_filter == 'public':
        my_courses = my_courses.filter(is_public=True)
    elif status_filter == 'private':
        my_courses = my_courses.filter(is_public=False)


    stats = {
        'total_my_courses': Course.objects.filter(user=request.user).count(),
        'total_public': Course.objects.filter(is_public=True).count(),
        'total_private': Course.objects.filter(is_public=False, user=request.user).count(),
        'total_all_courses': Course.objects.count(),
    }

    context = {
        'my_courses': my_courses,
        'all_courses': all_courses,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(request, 'course/course_list.html', context)

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
            return render(request, 'course/courses.html', {'form':form})
    form = CourseForm()
    return render(request, 'course/courses.html', {'form':form})


@login_required
def course_edit(request, course_id):


    course = get_object_or_404(Course, id=course_id, user=request.user)

    if request.method == 'POST':

        form = CourseForm(request.POST, instance=course)

        if form.is_valid():

            form.save()
            messages.success(request, f'✅ Course "{course.title}" updated successfully!')
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'course/courses.html', {
                'form': form,
                'course': course,
                'title': 'Edit Course'
            })


    form = CourseForm(instance=course)
    return render(request, 'course/courses.html', {
        'form': form,
        'course': course,
        'title': 'Edit Course'
    })

@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, user=request.user)

    if request.method == 'POST':
        course_title = course.title


        for note in course.notes.all():
            for file_obj in note.files.all():
                if file_obj.file:
                    try:
                        file_obj.file.delete(save=False)
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                file_obj.delete()
            note.delete()

        course.delete()
        messages.success(request, f' Course "{course_title}" deleted successfully!')
        return redirect('courses')

    return render(request, 'course/course_delete.html', {'course': course})

@login_required
def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)


    is_owner = (course.user == request.user)


    if not course.is_public and not is_owner:
        messages.error(request, "You don't have permission to view this course.")
        return redirect('course_list')


    if is_owner:
        notes = course.notes.all().order_by('-created_at')
    else:
        notes = course.notes.filter(is_public=True).order_by('-created_at')




    stats = {
        'total_notes': notes.count(),

        'public_notes': notes.filter(is_public=True).count(),
        'private_notes': notes.filter(is_public=False).count(),
    }

    context = {
        'course': course,
        'notes': notes,
        'stats': stats,
        'is_owner': is_owner,
    }

    return render(request, 'course/course_detail.html', context)

@login_required
def note_list(request):

    notes = Note.objects.filter(
        Q(is_public=True) | Q(user=request.user)
    ).order_by('-created_at')


    search_query = request.GET.get('search', '').strip()
    if search_query:
        notes = notes.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )


    course_filter = request.GET.get('course', '')
    if course_filter and course_filter.isdigit():
        notes = notes.filter(course_id=int(course_filter))


    paginator = Paginator(notes, 12)
    page = request.GET.get('page', 1)

    try:
        notes_page = paginator.page(page)
    except PageNotAnInteger:
        notes_page = paginator.page(1)
    except EmptyPage:
        notes_page = paginator.page(paginator.num_pages)


    courses = Course.objects.filter(user=request.user)


    total_notes = notes.count()
    public_notes = notes.filter(is_public=True).count()
    private_notes = notes.filter(is_public=False, user=request.user).count()
    notes_with_files = notes.filter(files__isnull=False).distinct().count()

    context = {
        'notes': notes_page,
        'courses': courses,
        'search_query': search_query,
        'course_filter': course_filter,
        'total_notes': total_notes,
        'public_notes': public_notes,
        'private_notes': private_notes,
        'notes_with_files': notes_with_files,
    }

    return render(request, 'notes/note_list.html', context)


@login_required
def note_download(request, file_id):

    file_obj = get_object_or_404(NoteFile, id=file_id)
    note = file_obj.note


    if not note.is_public and note.user != request.user:
        messages.error(request, "You don't have permission to download this file")
        return redirect('note_list')

    if not file_obj.file:
        messages.error(request, "File not found")
        return redirect('note_list')


    note.views_count += 1
    note.save()


    response = HttpResponse(file_obj.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_obj.original_filename}"'
    return response


@login_required
def note_create(request):
    if request.method == 'POST':



        form = NoteForm(
            request=request,
            data=request.POST,
            files=request.FILES
        )

        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()


            files = request.FILES.getlist('files')
            file_count = 0

            if files:
                for file in files:
                    try:
                        NoteFile.objects.create(
                            note=note,
                            file=file
                        )
                        file_count += 1
                        print(f"✅ File saved: {file.name}")
                    except Exception as e:
                        print(f"❌ Error saving file: {e}")
            else:
                print(" No files in request.FILES")

            messages.success(
                request,
                f'Note "{note.title}" created successfully with {file_count} file(s)!'
            )
            return redirect('note_list')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'notes/notes.html', {
                'form': form,
                'title': 'Create New Note'
            })

    form = NoteForm(request=request)
    return render(request, 'notes/notes.html', {
        'form': form,
        'title': 'Create New Note'
    })



@login_required
def note_delete_file(request, file_id):
    file_obj = get_object_or_404(NoteFile, id=file_id, note__user=request.user)
    note_id = file_obj.note.id

    if request.method == 'POST':
        try:
            filename = file_obj.original_filename
            file_obj.file.delete(save=False)
            file_obj.delete()
            messages.success(request, f'✅ File "{filename}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'❌ Error deleting file: {str(e)}')
        return redirect('note_edit', note_id=note_id)

    return render(request, 'notes/note_confirm_delete.html', {'file': file_obj})


@login_required
def note_delete_file(request, file_id):

    file_obj = get_object_or_404(NoteFile, id=file_id, note__user=request.user)
    note_id = file_obj.note.id

    if request.method == 'POST':
        try:
            filename = file_obj.original_filename


            if file_obj.file:
                file_obj.file.delete(save=False)


            file_obj.delete()

            messages.success(request, f' File "{filename}" deleted successfully!')
        except Exception as e:
            messages.error(request, f' Error deleting file: {str(e)}')

        return redirect('note_edit', note_id=note_id)


    return render(request, 'notes/file_confirm_delete.html', {'file': file_obj})


def note_detail(request, note_id):

    note = get_object_or_404(Note, id=note_id)


    if not note.is_public and note.user != request.user:
        messages.error(request, "You don't have permission to view this note.")
        return redirect('note_list')


    if note.user != request.user:
        note.views_count += 1
        note.save()

    context = {
        'note': note,
    }

    return render(request, 'notes/note_detail.html', context)


@login_required
def note_edit(request, note_id):

    note = get_object_or_404(Note, id=note_id, user=request.user)


    print("=" * 60)
    print(f"🔵 EDIT NOTE - User: {request.user.username}")
    print(f"📝 Note: {note.title} (ID: {note.id})")
    print(f"📚 Course: {note.course.title if note.course else 'None'}")
    print("=" * 60)

    if request.method == 'POST':
        print("🔵 POST request received")
        print(f"📁 FILES in request: {bool(request.FILES)}")
        print(f"📄 Files count: {len(request.FILES.getlist('files'))}")


        form = NoteForm(
            request=request,
            data=request.POST,
            files=request.FILES,
            instance=note
        )

        if form.is_valid():
            note = form.save()
            print(f"✅ Note saved: {note.title}")


            files = request.FILES.getlist('files')
            file_count = 0

            for file in files:
                try:
                    NoteFile.objects.create(
                        note=note,
                        file=file
                    )
                    file_count += 1
                    print(f"File saved: {file.name}")
                except Exception as e:
                    print(f"Error saving file: {e}")

            if file_count > 0:
                messages.success(request, f' {file_count} new file(s) added to "{note.title}"!')
            else:
                messages.success(request, f' Note "{note.title}" updated successfully!')

            return redirect('note_list')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'notes/note_edit.html', {
                'form': form,
                'note': note,
                'title': 'Edit Note'
            })


    form = NoteForm(
        instance=note,
        request=request
    )


    print(f"🔵 Form course queryset count: {form.fields['course'].queryset.count()}")

    return render(request, 'notes/note_edit.html', {
        'form': form,
        'note': note,
        'title': 'Edit Note'
    })


def main(request):

    public_courses = Course.objects.filter(is_public=True).order_by('-created_at')
    public_notes = Note.objects.filter(is_public=True).order_by('-created_at')

    context = {
        'public_courses': public_courses,
        'public_notes': public_notes,
    }


    if request.user.is_authenticated:
        context['my_courses'] = Course.objects.filter(user=request.user).order_by('-created_at')
        context['my_notes'] = Note.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'accounts/base.html', context)




















