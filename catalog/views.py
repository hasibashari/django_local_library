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
