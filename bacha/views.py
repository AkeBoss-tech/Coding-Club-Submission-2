from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Comment, Job, Product, Profile, Review, Transaction
from .forms import CommentForm, JobForm, JobPayForm, ProductForm, ReviewForm, TransactionForm, WithdrawForm, createUserForm, profileForm
from django.contrib.auth.decorators import login_required

BankUserID = 3

# Create your views here.
def registerPage(request):
    form = createUserForm(request.POST)
    profile_form = profileForm(request.POST)
    if request.method == 'POST':
        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            #we don't save the profile_form here because we have to first get the value of profile_form, assign the user to the OneToOneField created in models before we now save the profile_form. 

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.username = user.username

            profile.save()

            user.last_name = profile.last_name
            user.first_name = profile.first_name
            if profile.email:
                user.email = profile.email
            user.save()

            messages.success(request,  'Your account has been successfully created')

            return redirect('login')

    context = {'form': form, 'profile_form': profile_form}
    return render(request, 'register.html', context)

@login_required(login_url='/login/')
def editProfilePage(request):
    profile = Profile.objects.get(user=request.user)
    form = createUserForm(instance=profile.user)
    profile_form = profileForm(instance=profile)
    if request.method == 'POST':
        form = createUserForm(request.POST, instance=profile.user)
        profile_form = profileForm(request.POST, instance=profile)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()

            #we don't save the profile_form here because we have to first get the value of profile_form, assign the user to the OneToOneField created in models before we now save the profile_form. 

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.username = user.username

            profile.save()

            user.last_name = profile.last_name
            user.first_name = profile.first_name
            user.email = profile.email
            user.save()

            messages.success(request, 'Your account has been successfully created')

            return redirect('login')

    context = {'form': form, 'profile_form': profile_form}
    return render(request, 'register.html', context)

@login_required(login_url='/login/')
def userProfile(request, notification=''):
    print(request.user.username)
    profile = Profile.objects.get(user=request.user)

    transactions = []

    try:
        notif = len(Transaction.objects.get(receiver=profile, read=False))
    except:
        notif = 0

    for transaction in Transaction.objects.all().order_by('-time'):
        if transaction.payer == profile or transaction.receiver == profile:
            transactions.append(transaction)
            if transaction.read == False and transaction.receiver == profile:
                # Mark as read
                transaction.read = True
                transaction.save(update_fields=['read'])
        
        if len(transactions) >= 5:
            break
    
    jobs = []
    for job in Job.objects.all().order_by('-pay'):
        if job.employer == profile or profile in job.workers.all():
            jobs.append(job)
        
        if len(jobs) >= 5:
            break

    comment_dic = {}
    for comment in Comment.objects.all().order_by('-time'):
        comment_dic[comment] = Job.objects.get(comments=comment)

        if len(comment_dic) >= 5:
            break

    review_dic = {}
    for review in reversed(Review.objects.all()):
        review_dic[review] = Product.objects.get(reviews=review)
        
        if len(review_dic) >= 5:
            break

    products = []
    for product in Product.objects.all().order_by('-price'):
        if product.seller == profile or profile in product.buyers.all():
            products.append(product)
        
        if len(products) >= 5:
            break

    print(transactions)

    context = {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "full_name": " ".join([profile.first_name, profile.last_name]),
        "balance": profile.balance,
        "email": profile.email,
        "username": profile.username,
        "notification": notification,
        "transactions": transactions, 
        "len": len(transactions),
        "num_transactions": notif,
        'products': products,
        'product_len': len(products),
        'job_len': len(jobs),
        'jobs': jobs,
        'reviews': review_dic,
        'comments': comment_dic,
        'review_len': len(review_dic),
        'comment_len': len(comment_dic),
    }

    return render(request, 'home.html', context)

@login_required(login_url='/login/')
def SuccessProfile(request):
    return userProfile(request, 'Success')

@login_required(login_url='/login/')
def transactionForm(request):
    profile = Profile.objects.get(user=request.user)
    form = TransactionForm(request.POST)
    if request.method == 'POST':
        print(form)
        if form.is_valid():
            userKey = profile.id
            form.instance.payer_id = userKey

            if not (form.clean_from_sender(form.instance.receiver.id, userKey) and form.is_valid()):
                context = {'form': form, 'title': 'Transaction Form'}
                return render(request, 'form.html', context)

            """ t = Transaction(payer_id = userKey, receiver=form.cleaned_data.get('receiver'), description=form.cleaned_data.get('description'), amount=form.cleaned_data.get('amount'))
            messages.success(request,  'Your transaction has been successfully created')
            t.save() """

            payer = Profile.objects.get(id=profile.id)
            receiver = Profile.objects.get(id=form.instance.receiver.id)
            print(payer)
            payer.balance -= form.instance.amount
            receiver.balance += form.instance.amount

            try:
                payer.save(update_fields=['balance'])
                receiver.save(update_fields=['balance'])
                form.save()
                messages.success(request, 'Your transaction has been successfully run')
            except:
                context = {'form': form, 'title': 'Transaction Form', 'notification': 'Failure'}
                return render(request, 'form.html', context)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    context = {'form': form, 'title': 'Transaction Form'}
    return render(request, 'form.html', context)

@login_required(login_url='/login/')
def withdrawForm(request):
    profile = Profile.objects.get(user=request.user)
    form = WithdrawForm(request.POST)
    if request.method == 'POST':
        print(form)
        if form.is_valid():
            userKey = profile.id
            form.instance.receiver_id = userKey
            form.instance.payer_id = userKey
            form.instance.description = f'Withdrawl for {form.instance.amount}'

            payer = Profile.objects.get(id=profile.id)
            payer.balance -= form.instance.amount

            try:
                payer.save(update_fields=['balance'])
                form.save()
                messages.success(request, 'Your transaction has been successfully run')
            except:
                context = {'form': form, 'title': 'Withdrawl Form', 'notification': 'Failure'}
                return render(request, 'form.html', context)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    context = {'form': form, 'title': 'Withdrawl Form'}
    return render(request, 'form.html', context)

@login_required(login_url='/login/')
def depositForm(request):
    profile = Profile.objects.get(user=request.user)
    form = WithdrawForm(request.POST)
    if request.method == 'POST':
        print(form)
        if form.is_valid():
            userKey = profile.id
            form.instance.receiver_id = userKey
            form.instance.payer_id = userKey
            form.instance.description = f'Withdrawl for {form.instance.amount}'

            payer = Profile.objects.get(id=profile.id)
            payer.balance += form.instance.amount

            try:
                payer.save(update_fields=['balance'])
                form.save()
                messages.success(request, 'Your transaction has been successfully run')
            except:
                context = {'form': form, 'title': 'Deposit Form', 'notification': 'Failure'}
                return render(request, 'form.html', context)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    context = {'form': form, 'title': 'Deposit Form'}
    return render(request, 'form.html', context)

@login_required(login_url='/login/')
def TransactionView(request, id):
    profile = Profile.objects.get(user=request.user)
    transaction = get_object_or_404(Transaction, id=id)
    if transaction.payer == profile or transaction.receiver == profile:
        context = {
            'transaction': transaction,
            'time': transaction.time
        }
        if transaction.read == False and transaction.receiver == profile:
                # Mark as read
                transaction.read = True
                transaction.save(update_fields=['read'])
        return render(request, 'transaction.html', context)
    return render(request, 'blank.html', {'text': 'You do not have access to these details'})

@login_required(login_url='/login/')
def TransactionsView(request):
    profile = Profile.objects.get(user=request.user)
    transactions = []
    for transaction in Transaction.objects.all().order_by('-time'):
        if transaction.payer == profile or transaction.receiver == profile:
            transactions.append(transaction)
            if transaction.read == False and transaction.receiver == profile:
                # Mark as read
                transaction.read = True
                transaction.save(update_fields=['read'])

    context = {
        'transactions': transactions,
        'len': len(transactions)
    }
    return render(request, 'transactions.html', context)

@login_required(login_url='/login/')
def CreateJobForm(request):
    profile = Profile.objects.get(user=request.user)
    form = JobForm(request.POST)
    if request.method == 'POST':
        print(form)
        if form.is_valid():
            form.instance.employer_id = profile.id

            try:
                form.save()
                messages.success(request, 'Your job has been successfully created')
            except:
                context = {'form': form, 'title': 'Job Creation Form', 'notification': 'Failure'}
                return render(request, 'form.html', context)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    context = {'form': form, 'title': 'Job Creation Form'}
    return render(request, 'form.html', context)

@login_required(login_url='/login/')
def JobView(request, id):
    profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.commenter = profile
            form.save()
            form_id = form.instance.id
            comment = Comment.objects.get(id=form_id)
            job.comments.add(comment)

    form = CommentForm()
    if job.availability or (job.employer == profile or profile in job.workers.all()):
        context = {
            'job': job,
            'form': form
        }
        return render(request, 'job.html', context)
    return render(request, 'blank.html', {'text': 'You do not have access to these details'})

@login_required(login_url='/login/')
def editJobView(request, id):
    profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=id)
    form = JobForm(instance=job)

    if job.employer == profile:
        if request.method == 'POST':
            form = JobForm(request.POST, instance=job)
            print(form.is_valid())
            if form.is_valid():
                print("yes")
                form.instance.employer_id = profile.id
                form.save()
                try:
                    form.save()
                    print("updated")
                    messages.success(request, 'Your job has been edited created')
                except:
                    context = {'form': form, 'title': 'Job Creation Form', 'notification': 'Failure'}
                    return render(request, 'form.html', context)
                return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

        context = {'form': form, 'title': 'Job Edit Form'}
        return render(request, 'form.html', context)
    return render(request, 'blank.html', {'text': 'You do not have access to these details'})

@login_required(login_url='/login/')
def JobSearch(request):
    profile = Profile.objects.get(user=request.user)
    jobs = []
    for job in Job.objects.all().order_by('-pay'):
        print(job.workers.all)
        f = job.workers.all
        if not (job.employer == profile or profile in job.workers.all()):
            jobs.append(job)

    context = {
        'jobs': jobs
    }
    return render(request, 'job_search.html', context)

@login_required(login_url='/login/')
def JobJoin(request, id):
    profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=id)
    if job.employer == profile or profile in job.workers.all():
        return render(request, 'blank.html', {'text': 'You do not have access to this page'})
    
    if request.method == 'POST':
        job.workers.add(profile)
        job.save()
        return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))
    return render(request, 'sure.html', {'text': 'Click this button to join'})

@login_required(login_url='/login/')
def JobLeave(request, id):
    profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=id)
    if not (job.employer == profile or profile in job.workers.all()):
        return render(request, 'blank.html', {'text': 'You do not have access to this page'})
    
    if request.method == 'POST':
        if job.employer == profile:
            for comment in job.comments.all():
                comment.delete()
            
            job.delete()
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))
        elif profile in job.workers.all():
            job.workers.remove(profile)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    if job.employer == profile:
        return render(request, 'sure.html', {'text': 'Click this button to delete the job'})
    elif profile in job.workers.all():
        return render(request, 'sure.html', {'text': 'Click this button to leave'})
    return render(request, 'blank.html', {'text': 'I am not sure how you are here'})

@login_required(login_url='/login/')
def JobPay(request, id):
    profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(Job, id=id)
    if not job.employer == profile:
        return render(request, 'blank.html', {'text': 'You do not have access to this page'})
    
    if job.workers.all().count() == 0:
        return render(request, 'blank.html', {'text': 'You do not have access to this page. Please get some workers'})

    form = JobPayForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            bonus = form.cleaned_data['bonus']
            comment = form.cleaned_data['comment']

            # First Employer gets the stimulus
            profile.balance += int(job.minutes * (1 + job.workers.count()))

            stimulus = Transaction(payer=Profile.objects.get(id=BankUserID), receiver=profile, description=f'Stimulus for Job: {job.name}', amount = int(job.minutes * (1 + job.workers.count())))

            try:
                profile.save(update_fields=['balance'])
                stimulus.save()
                job.transactions.add(stimulus)
                messages.success(request, 'Your transaction has been successfully run')
            except:
                context = {
                    'text': "The Form Failed",
                    'stimulus': str(job.minutes * (1 + job.workers.count())),
                    'price': str(job.pay * job.workers.count()),
                    'form': form,
                    'notification': 'Failure'
                }
                return render(request, 'pay_workers.html', context)

            for worker in job.workers.all():
                profile.balance -= int(bonus + job.pay)
                worker.balance += int(bonus + job.pay)
                pay = Transaction(payer=profile, receiver=worker, description=f'Pay from {job.name}: {comment}', amount = int(bonus+job.pay))
                try:
                    profile.save(update_fields=['balance'])
                    worker.save(update_fields=['balance'])
                    pay.save()
                    job.transactions.add(pay)
                    messages.success(request, 'Your transaction has been successfully run')
                except:
                    context = {
                        'text': "The form Failed",
                        'stimulus': str(job.minutes * (1 + job.workers.count())),
                        'price': str(job.pay * job.workers.count()),
                        'form': form,
                        'notification': 'Failure'
                    }
                    return render(request, 'pay_workers.html', context)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    context = {
        'text': "Please Submit this form to pay workers",
        'stimulus': str(job.minutes * (1 + job.workers.count())),
        'price': str(job.pay * job.workers.count()),
        'form': form
    }
    return render(request, 'pay_workers.html', context)

@login_required(login_url='/login/')
def JobsView(request):
    profile = Profile.objects.get(user=request.user)
    jobs = []
    for job in Job.objects.all().order_by('-pay'):
        if job.employer == profile or profile in job.workers.all():
            jobs.append(job)

    context = {
        'jobs': jobs,
        'job_len': len(jobs)
    }
    return render(request, 'jobs.html', context)


# Shop

@login_required(login_url='/login/')
def CreateProductForm(request):
    profile = Profile.objects.get(user=request.user)
    form = ProductForm(request.POST)
    if request.method == 'POST':
        print(form)
        if form.is_valid():
            form.instance.seller_id = profile.id

            try:
                form.save()
                messages.success(request, 'Your product has been successfully created')
            except:
                context = {'form': form, 'title': 'Product Creation Form', 'notification': 'Failure'}
                return render(request, 'form.html', context)
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    context = {'form': form, 'title': 'Product Creation Form'}
    return render(request, 'form.html', context)

@login_required(login_url='/login/')
def ProductView(request, id):
    profile = Profile.objects.get(user=request.user)
    product = get_object_or_404(Product, id=id)

    form_is_possible = False
    if profile in product.buyers.all() and not profile in [review.commenter for review in product.reviews.all()]:
        form_is_possible = True

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid() and form_is_possible:
            form.instance.commenter = profile
            form.save()
            form_id = form.instance.id
            review = Review.objects.get(id=form_id)
            product.reviews.add(review)

    form = ReviewForm()
    
    context = {
        'product': product,
        'form': form,
        'form_is_possible': form_is_possible
    }
    return render(request, 'product.html', context)
    # return render(request, 'blank.html', {'text': 'You do not have access to these details'})

@login_required(login_url='/login/')
def editProductView(request, id):
    profile = Profile.objects.get(user=request.user)
    product = get_object_or_404(Product, id=id)
    form = ProductForm(instance=product)

    if product.seller == profile:
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            print(form.is_valid())
            if form.is_valid():
                print("yes")
                form.instance.employer_id = profile.id
                try:
                    form.save()
                    print("updated")
                    messages.success(request, 'Your product has been edited created')
                except:
                    context = {'form': form, 'title': 'Product Edit Form', 'notification': 'Failure'}
                    return render(request, 'form.html', context)
                return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

        context = {'form': form, 'title': 'Product Edit Form'}
        return render(request, 'form.html', context)
    return render(request, 'blank.html', {'text': 'You do not have access to these details'})

@login_required(login_url='/login/')
def ProductSearch(request):
    products = []
    for product in Product.objects.all().order_by('-availability'):
        products.append(product)

    context = {
        'products': products,
        'product_len': len(products)
    }
    return render(request, 'product_search.html', context)

@login_required(login_url='/login/')
def ProductBuy(request, id):
    profile = Profile.objects.get(user=request.user)
    product = get_object_or_404(Product, id=id)
    if product.seller == profile:
        return render(request, 'blank.html', {'text': 'You do not have access to this page'})
    
    if product.availability <= 0:
        return render(request, 'blank.html', {'text': 'Item is sold out'})

    if request.method == 'POST':
        # First Employer gets the money
        profile.balance -= int(product.price)
        seller = product.seller
        seller.balance += int(product.price)

        buy = Transaction(payer=profile, receiver=seller, description=f'Item Sold: {product.name}', amount = int(product.price))

        try:
            profile.save(update_fields=['balance'])
            buy.save()
            seller.save(update_fields=['balance'])
            product.transactions.add(buy)
            if not profile in product.buyers.all():
                product.buyers.add(profile)
            product.availability -= 1
            product.save()
            messages.success(request, 'Your transaction has been successfully run')
        except:
            return render(request, 'sure.html', {'text': 'Purchase Failed. Click this button to buy'})

        
        return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    return render(request, 'sure.html', {'text': 'Click this button to buy'})

@login_required(login_url='/login/')
def ProductsView(request):
    profile = Profile.objects.get(user=request.user)
    products = []
    for product in Product.objects.all().order_by('-price'):
        if product.seller == profile or profile in product.buyers.all():
            products.append(product)

    context = {
        'products': products,
        'product_len': len(products)
    }
    return render(request, 'products.html', context)

@login_required(login_url='/login/')
def ProductDelete(request, id):
    profile = Profile.objects.get(user=request.user)
    product = get_object_or_404(Product, id=id)
    if not product.seller == profile:
        return render(request, 'blank.html', {'text': 'You do not have access to this page'})
    
    if request.method == 'POST':
        if product.seller == profile:
            for review in product.reviews.all():
                review.delete()
            
            product.delete()
            return HttpResponseRedirect(reverse('homeWithNotif', args=['Success']))

    return render(request, 'sure.html', {'text': 'Click this button to delete the product'})

def justBase(request):
    return render(request, 'base.html')
