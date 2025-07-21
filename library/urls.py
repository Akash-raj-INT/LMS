from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book-list'),
    path('add-book/', views.add_book, name='add-book'),
    path('members/', views.member_list, name='member-list'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow-book'),
    path('return/<int:loan_id>/', views.return_book, name='return-book'),
    path('loans/', views.loan_list, name='loan-list'),
    path('fines/', views.fine_list, name='fine-list'),
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('delete-member/<int:member_id>/', views.delete_member, name='delete_member'),
    path('edit-book/<int:book_id>/', views.edit_book, name='edit-book'),
]
