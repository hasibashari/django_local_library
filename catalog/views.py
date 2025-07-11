from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Author
from django.urls import reverse_lazy
from catalog.forms import RenewBookForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Book, BookInstance, Author, Genre, Language
from django.shortcuts import render
from django.views import generic

# Create your views here.


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    num_authors = Author.objects.count()  # The 'all()' is implied by default

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    search_word_book = 'programming'
    search_word_genre = 'Science Fiction'

    # filter books by title containing 'programing'
    num_books_containing_word = Book.objects.filter(
        title__icontains=search_word_book).count()
    # filter books by genre containing 'self-improvement'
    num_genres_containing_word = Genre.objects.filter(
        name__icontains=search_word_genre).count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_containing_word': num_books_containing_word,
        'search_word_book': search_word_book,
        'num_genres_containing_word': num_genres_containing_word,
        'search_word_genre': search_word_genre,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    # Specify your own template name/location
    template_name = 'catalog/book_list.html'
    context_object_name = 'book_list'  # Default is 'object_list'
    paginate_by = 2  # Number of books to display per page


class BookDetailView(generic.DetailView):
    model = Book
    # Specify your own template name/location
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'  # Default is 'object'


class AuthorListView(generic.ListView):
    model = Author
    # Specify your own template name/location
    template_name = 'catalog/author_list.html'
    context_object_name = 'author_list'  # Default is 'object_list'


class AuthorDetailView(generic.DetailView):
    model = Author
    # Specify your own template name/location
    template_name = 'catalog/author_detail.html'
    context_object_name = 'author'  # Default is 'object'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all borrowed books. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    # You may want to create a separate template
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    initial = {'summary': 'This is a summary of the book.'}
    permission_required = 'catalog.add_book'

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.pk})


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_book'

    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.pk})


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )
