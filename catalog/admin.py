from django.contrib import admin
# Import your models here
from .models import Author, Book, BookInstance, Genre, Language

# Register your models here.
# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)


# Tabular Inline for Book
class BooksInline(admin.TabularInline):
    """Define the inline admin interface for Book model."""
    model = Book
    extra = 0  # Number of empty forms to display

class AuthorAdmin(admin.ModelAdmin):
    """Define the admin interface for Author model."""
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    # Adding Fields to the AuthorAdmin
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

    inlines = [BooksInline]  # Add the inline for books


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('book','status', 'due_back','id')

    # add fields to the admin interface
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )




# Register the Author model with the custom admin interface
admin.site.register(Author, AuthorAdmin)

