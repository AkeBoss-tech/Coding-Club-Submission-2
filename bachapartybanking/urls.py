"""bachapartybanking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from bacha.views import CreateProductForm, ProductBuy, ProductDelete, ProductSearch, ProductView, ProductsView, editProductView
from bacha.views import registerPage, userProfile, justBase, transactionForm, TransactionView, TransactionsView, CreateJobForm, JobView, editJobView, editProfilePage, JobSearch, JobJoin, JobLeave, JobPay, JobsView
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

from bachapartybanking.bacha.views import depositForm, withdrawForm

urlpatterns = [
    # Auth
    path('admin/', admin.site.urls, name='admin'),
    path('signup/', registerPage, name='signup'),
    path('user/edit', editProfilePage, name='edit-profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')), 
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # Homes
    path('home/', userProfile, name='home'),
    path('user/home/<str:notification>', userProfile, name='homeWithNotif'),
    path('', userProfile, name='Landing'),
    path('base/', justBase, name='base'),

    # Transactions
    path('view/transaction/<int:id>', TransactionView, name='transaction'),
    path('user/transaction', transactionForm, name='runTransaction'),
    path('user/transactions', TransactionsView, name="transactions"),

    # jobs
    path('user/job', CreateJobForm, name="create_job"),
    path('view/job/<int:id>', JobView, name='view_job'),
    path('join/job/<int:id>', JobJoin, name='join_job'),
    path('leave/job/<int:id>', JobLeave, name='leave_job'),
    path('pay/job/<int:id>', JobPay, name='pay_job'),
    path('user/jobs', JobsView, name='jobs'),
    path('search/job/', JobSearch, name='search_jobs'),
    path('view/job/edit/<int:id>', editJobView, name='job_edit'),

    # Products
    path('user/product', CreateProductForm, name="create_product"),
    path('view/product/<int:id>', ProductView, name='view_product'),
    path('delete/product/<int:id>', ProductDelete, name='delete_product'),
    path('buy/product/<int:id>', ProductBuy, name='buy_product'),
    path('user/products', ProductsView, name='products'),
    path('search/products/', ProductSearch, name='search_products'),
    path('edit/product/<int:id>', editProductView, name='product_edit'),

    # Favicon
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),name="favicon.ico"),

    # Deposit & Withdrawl
    path('user/deposit', depositForm, name='Deposit Money'),
    path('user/withdraw', withdrawForm, name='Withdraw Money'),
]
