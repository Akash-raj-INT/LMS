from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Book, Member, Loan, Fine
from .forms import BookForm, LoanForm, RegisterForm
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            member_type = form.cleaned_data['member_type']
            Member.objects.create(user=user, member_type=member_type)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'library/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'library/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    total_loans = Loan.objects.count()
    total_fines = Fine.objects.count()
    unpaid_fines = Fine.objects.filter(paid=False).count() if hasattr(Fine, 'paid') else 0
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'total_loans': total_loans,
        'total_fines': total_fines,
        'unpaid_fines': unpaid_fines,
    }
    return render(request, 'library/dashboard.html', context)

@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.copies_available = book.copies_total
            book.save()
            messages.success(request, 'Book added successfully!')
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book-list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'edit_mode': True, 'book': book})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book-list')
    return render(request, 'library/delete_book.html', {'book': book})

@login_required
def member_list(request):
    members = Member.objects.all()
    return render(request, 'library/member_list.html', {'members': members})

@login_required
def delete_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    active_loans = member.get_active_loans()
    if active_loans.exists():
        name = member.user.get_full_name() if member.user else 'Unknown'
        messages.error(request, f'Cannot delete {name}. They have {active_loans.count()} active loan(s). Please return all books first.')
        return redirect('member-list')
    if request.method == 'POST':
        # Save name for message before deleting
        name = member.user.get_full_name() if member.user else 'Unknown'
        member.delete()
        messages.success(request, f'Member {name} deleted successfully!')
        return redirect('member-list')
    return render(request, 'library/delete_member.html', {'member': member})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if not book.is_available():
        messages.error(request, 'This book is not available for borrowing.')
        return redirect('book-list')
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.book = book
            loan.loan_date = date.today()
            try:
                loan.full_clean()
                if book.borrow_copy():
                    loan.save()
                    messages.success(request, f'Book "{book.title}" borrowed successfully by {loan.member.user.get_full_name()}')
                    return redirect('book-list')
                else:
                    messages.error(request, 'Book is no longer available.')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    else:
        form = LoanForm(initial={'book': book})
    return render(request, 'library/loan_form.html', {'form': form, 'book': book})

@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    if request.method == 'POST':
        fine_amount = loan.return_book()
        if fine_amount > 0:
            messages.warning(request, f'Book returned successfully. Fine of ₹{fine_amount} has been applied for overdue return.')
        else:
            messages.success(request, 'Book returned successfully!')
        return redirect('loan-list')
    return render(request, 'library/return_book.html', {'loan': loan})

@login_required
def loan_list(request):
    loans = Loan.objects.all().order_by('-loan_date')
    return render(request, 'library/loan_list.html', {'loans': loans})

@login_required
def fine_list(request):
    fines = Fine.objects.all()
    return render(request, 'library/fine_list.html', {'fines': fines})

@login_required
def pay_fine(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)
    if request.method == 'POST':
        fine.mark_as_paid()
        messages.success(request, f'Fine of ₹{fine.amount} marked as paid.')
        return redirect('fine-list')
    return render(request, 'library/pay_fine.html', {'fine': fine})

