from django.http import HttpResponseRedirect
from django.shortcuts import render,HttpResponse
from django.urls import reverse
from .models import register,expense_store,MonthlyLimit
from django.shortcuts import redirect,get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime


# Create your views here.
def home(request):                       #goes to the register page
    return render(request,"register.html")

def login(request):                        #this goes to the login from the link
    return render(request,"login.html")

def add(request):                               #will add expenses
    return render(request,"add.html")
    
def jan(request):                          
      return render(request,"jan.html")


def paginate_queryset(request, queryset, per_page=10): #pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    return {
        "key": page_obj.object_list,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
    }


def dashboard(request):  
    # Check if user is logged in
    if 'username' not in request.session:
        return redirect('logins')  # Redirect to login page

    current_username = request.session['username']
    
    try:
        current_user = register.objects.get(username=current_username)
    except register.DoesNotExist:
        return redirect('logins')  # Extra safety: if user record not found

    data = expense_store.objects.filter(user=current_user).order_by('-date')

    context = paginate_queryset(request, data)
    context["current_user"] = current_user

    return render(request, "dashboard.html", context)


def registered(request):  # Register page
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        confirm_password = request.POST.get('password1')

        if password == confirm_password:
            # You should validate that the user doesn't already exist
            if register.objects.filter(username=username).exists():
                return HttpResponse("Username already exists")

            new_user = register(username=username, email=email, password=password, password1=confirm_password)
            new_user.save()
            return render(request, "login.html")
        else:
            return HttpResponse("Passwords do not match")
    
    return render(request, "register.html") 


def logins(request):

    # If already logged in, redirect to dashboard
    if 'username' in request.session:
        return redirect('dashboard')

    if request.method == "POST":
        user = request.POST.get('username1')
        passs = request.POST.get('password2')

        matched_user = register.objects.filter(username=user, password1=passs).first()

        if matched_user:
            # Store username in session
            request.session['username'] = matched_user.username           
            return redirect('dashboard')
        else:
            return HttpResponse("Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()  # This clears all session data
    return redirect('login')  # Redirect to your login page or home


def expenses(request):
    print("DEBUG: View called")

    if 'username' not in request.session:
        return redirect('logins')
    
    current_username = request.session['username']
    try:
        current_user = register.objects.get(username=current_username)
    except register.DoesNotExist:
        return redirect('logins')

    if request.method == "POST":
        dates = request.POST.get('date')
        amounts = request.POST.get('amount')
        modes = request.POST.get('mode')
        categorys = request.POST.get('category')

        print(f"DEBUG: Received - Date: {dates}, Amount: {amounts}, Mode: {modes}, Category: {categorys}")

        if not all([dates, amounts, modes, categorys]):
            return HttpResponse("⚠️ Missing data in form. Please fill all fields.")

        try:
            amounts = float(amounts)
        except ValueError:
            return HttpResponse("❌ Invalid amount format")

        # Parse the date to extract month and year
        try:
            date_obj = datetime.strptime(dates, '%Y-%m-%d')
        except ValueError:
            return HttpResponse("❌ Invalid date format")

        month = date_obj.month
        year = date_obj.year

        # Get total expenses for this month
        total_spent = expense_store.objects.filter(
            user=current_user,
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Check limit (if exists)
        limit_obj = MonthlyLimit.objects.filter(user=current_user, month=month, year=year).first()
        if limit_obj:
            future_total = total_spent + amounts
            limit_amount = limit_obj.amount
        
            if future_total > limit_amount:
                messages.error(request, "❌ Monthly limit exceeded. Expense not added.")
                return redirect('add')
        
            elif future_total >= 0.8 * limit_amount:
                messages.warning(request, "⚠️ You’ve used over 80% of your monthly limit!")

        # Save the expense
        datas = expense_store(user=current_user, date=dates, amount=amounts, mode=modes, category=categorys)
        datas.save()
        print("DEBUG: Expense saved successfully")
        messages.success(request, "✅ Expense added successfully.")
        return HttpResponseRedirect(reverse("dashboard"))

    return redirect('add')



def filter_month(request):
    if 'username' not in request.session:
        return redirect('logins')

    current_user = register.objects.get(username=request.session['username'])
    month = request.GET.get('month')
    qs = expense_store.objects.filter(user=current_user)

    if month:
        try:
            qs = qs.filter(date__month=int(month))
        except:
            return HttpResponse("Invalid month")

    # 👇 Aggregate total spent per category
    category_totals = qs.values('category').annotate(total=Sum('amount'))

    # 👇 Prepare data for chart
    labels = [item['category'] for item in category_totals]
    values = [item['total'] for item in category_totals]

    total_amount = sum(values)
    percentages = [(v / total_amount) * 100 if total_amount else 0 for v in values]

    context = {
        "key": qs,
        "selected_month": month,
        "current_user": current_user,
        "chart_labels": labels,
        "chart_values": percentages,
        'total_amount': total_amount,
    }

    return render(request, "jan.html", context)

def update(request, id):
    data = expense_store.objects.get(id=id)
    return render(request, "update.html", {'data': data})


def update_submit(request, id):
    if 'username' not in request.session:
        return redirect('logins')

    current_username = request.session['username']
    try:
        current_user = register.objects.get(username=current_username)
    except register.DoesNotExist:
        return redirect('logins')

    if request.method == "POST":
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        mode = request.POST.get('mode')
        category = request.POST.get('category')

        if not all([date, amount, mode, category]):
            return HttpResponse("⚠️ Missing data in form. Please fill all fields.")

        try:
            amount = float(amount)
        except ValueError:
            return HttpResponse("❌ Invalid amount format")

        # Parse date
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return HttpResponse("❌ Invalid date format")

        month = date_obj.month
        year = date_obj.year

        # Get the original expense
        expense = get_object_or_404(expense_store, id=id, user=current_user)

        # Get total spent in the month (excluding this expense)
        total_spent = expense_store.objects.filter(
            user=current_user,
            date__month=month,
            date__year=year
        ).exclude(id=expense.id).aggregate(total=Sum('amount'))['total'] or 0

        # Check monthly limit
        limit_obj = MonthlyLimit.objects.filter(user=current_user, month=month, year=year).first()
        if limit_obj:
            future_total = total_spent + amount
            if future_total > limit_obj.amount:
                messages.error(request, "❌ Cannot update. Monthly limit would be exceeded.")
                return redirect('dashboard')
            elif future_total >= 0.8 * limit_obj.amount:
                messages.warning(request, "⚠️ You’ve used over 80% of your monthly limit!")

        # All good — update the expense
        expense.date = date
        expense.amount = amount
        expense.mode = mode
        expense.category = category
        expense.save()

        messages.success(request, "✅ Expense updated successfully.")
        return redirect('dashboard')

    return redirect('dashboard')



def delete_expense(request, id):
    if 'username' not in request.session:
        return redirect('logins')

    current_username = request.session['username']
    try:
        current_user = register.objects.get(username=current_username)
    except register.DoesNotExist:
        return redirect('logins')

    expense = get_object_or_404(expense_store, id=id, user=current_user)
    expense.delete()
    messages.success(request, "🗑️ Expense deleted successfully.")
    return redirect('dashboard')


def set_limit(request):
    if 'username' not in request.session:
        return redirect('logins')

    current_username = request.session['username']
    try:
        current_user = register.objects.get(username=current_username)
    except register.DoesNotExist:
        return redirect('logins')

    if request.method == "POST":
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except ValueError:
            return HttpResponse("❌ Invalid amount")

        month = timezone.now().month
        year = timezone.now().year

        # Total spent already this month
        total_spent = expense_store.objects.filter(
            user=current_user,
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Check if a limit already exists
        existing_limit = MonthlyLimit.objects.filter(
            user=current_user,
            month=month,
            year=year
        ).first()

        if existing_limit:
            if amount < existing_limit.amount:
                messages.error(request, f"❌ Cannot lower limit. Current limit is ₹{existing_limit.amount}")
                return redirect('dashboard')
            if amount < total_spent:
                messages.error(request, f"❌ Cannot set limit below your total spent amount (₹{total_spent}).")
                return redirect('dashboard')

            # Update the limit (increased)
            existing_limit.amount = amount
            existing_limit.save()
            messages.success(request, "✅ Limit updated successfully.")
        else:
            # First-time limit
            if amount < total_spent:
                messages.error(request, f"❌ Cannot set limit below your total spent amount (₹{total_spent}).")
                return redirect('dashboard')

            MonthlyLimit.objects.create(
                user=current_user,
                month=month,
                year=year,
                amount=amount
            )
            messages.success(request, "✅ Monthly limit set successfully.")

        return redirect('dashboard')

    return redirect('dashboard')
