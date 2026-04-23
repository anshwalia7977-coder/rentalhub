#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib import messages
from .models import UserInfo
from django.core.mail import send_mail
import random



from django.contrib.auth.hashers import make_password

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until verified
            user.otp = str(random.randint(100000, 999999))
            user.save()

            # Send OTP email
            send_mail(
                subject='Email Verification - OTP Code',
                message=f'Hi {user.username},\n\nYour OTP code is: {user.otp}',
                from_email='your_email@gmail.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Store user id in session to retrieve in OTP view
            request.session['user_id'] = user.id
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect('verify_otp')
    else:
        form = SignUpForm()
    
    return render(request, 'signup/register.html', {'form': form})

from .forms import LoginForm  # if you're using the custom form

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import UserInfo

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_obj = UserInfo.objects.get(username=username)
        except UserInfo.DoesNotExist:
            user_obj = None

        if user_obj:
            # Case 1: user exists but not verified
            if not user_obj.is_active:
                request.session['user_id'] = user_obj.id
                messages.error(request, "Your email is not verified. Please verify it before login.")
                return redirect('login')

            # Case 2: user is active → check password
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'signup/login.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard_view(request):
    user = request.user 
    return render(request, 'signup/dashboard.html', {'user': user})

from .forms import EditProfileForm
@login_required
def edit_profile(request):
    user = request.user  # current logged-in user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # go back to dashboard after saving
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'signup/edit_profile.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render
from .models import UserInfo

def verify_otp_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "No user found in session.")
        return redirect('signup')

    user = UserInfo.objects.get(id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        if entered_otp == user.otp:
            user.is_active = True
            user.otp = None
            user.save()
            messages.success(request, "Your email has been verified. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'signup/verify_otp.html', {'email': user.email})

from django.views.decorators.http import require_POST

@require_POST
def resend_otp_view(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "No user found in session.")
        return redirect('signup')

    user = UserInfo.objects.get(id=user_id)
    user.otp = str(random.randint(100000, 999999))
    user.save()

    send_mail(
        subject='Resend OTP - Email Verification',
        message=f'Hi {user.username},\n\nYour new OTP code is: {user.otp}',
        from_email='your_email@gmail.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp')

from .models import Product

@login_required
def product_list_view(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'signup/product_list.html', {'products': products})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Rental

@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.available:
        messages.error(request, "❌ This product is currently not available for rental.")
        return redirect('product_detail', product_id=product.id)

    if request.method == "POST":
        rental_days = int(request.POST.get("rental_days", 1))
        delivery_address = request.POST.get("delivery_address", "")

        CartItem.objects.create(
            user=request.user,
            product=product,
            rental_days=rental_days,
            delivery_address=delivery_address
        )

        messages.success(request, "✅ Product added to your cart successfully.")
        return redirect('product_list')

    return redirect('product_detail', product_id=product.id)


@login_required
def view_cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'signup/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart_view(request, item_id):
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    return redirect('view_cart')

from django.contrib import messages
from django.utils import timezone
from .models import CartItem, Rental

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "⚠ Your cart is empty.")
        return redirect('view_cart')

    for item in cart_items:
        if not item.product.available:
            messages.error(request, f"❌ Product '{item.product.name}' is no longer available.")
            return redirect('view_cart')

        # Create Rental record
        Rental.objects.create(
            user=request.user,
            product=item.product,
            rental_days=item.rental_days,
            delivery_address=item.delivery_address
        )

        # Mark product as unavailable
        item.product.available = False
        item.product.save()

    cart_items.delete()
    messages.success(request, "✅ Rental confirmed successfully!")
    return render(request, 'signup/checkout_success.html', {'user': request.user})
                                                            
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from datetime import timedelta
from .models import Product, Rental

@login_required
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    active_rentals = Rental.objects.filter(product=product)

    # Check if any rental is still active (i.e., not expired yet)
    available = True
    now = timezone.now()
    for rental in active_rentals:
        return_date = rental.rented_at + timedelta(days=rental.rental_days)
        if return_date >= now:
            available = False
            break

    return render(request, 'signup/product_detail.html', {
        'product': product,
        'available': available
    })

@login_required
def my_rentals_view(request):
    rentals = Rental.objects.filter(user=request.user).select_related("product")
    return render(request, 'signup/my_rentals.html', {'rentals': rentals})

 