from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/',views.dashboard_view, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/',views.resend_otp_view, name='resend_otp'),
    path('products/', views.product_list_view, name='product_list'),
    path('cart/', views.view_cart_view, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('my-rentals/', views.my_rentals_view, name='my_rentals'),
    # 1. User enters email
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name="signup/password_reset.html"
    ), name="password_reset"),

    # 2. Django shows confirmation "email sent"
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="signup/password_reset_done.html"
    ), name="password_reset_done"),

    # 3. User clicks link from email → opens reset form
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="signup/password_reset_confirm.html"
    ), name="password_reset_confirm"),

    # 4. After success, show "Password reset complete"
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name="signup/password_reset_complete.html"
    ), name="password_reset_complete"),

]