# accounts/views.py
from django.views.generic import (
    CreateView,
    UpdateView,
    DetailView,
    TemplateView,
    FormView,
    DeleteView
)
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    AccountDeleteForm,
    UserLoginForm
)
from .models import CustomUser, UserProfile


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()

        # Optional: Login otomatis setelah registrasi
        login(self.request, user)

        return super().form_valid(form)


class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('profile')


class CustomLogoutView(LogoutView):
    next_page = 'login'


class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.userprofile


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.userprofile


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')


class PasswordResetRequestView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class EmailVerificationView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/email_verify.html'


class EmailVerificationConfirmView(TemplateView):
    template_name = 'accounts/email_verify_confirm.html'


class AccountSecurityView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_security.html'


class ConnectedDevicesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/connected_devices.html'


class LoginHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/login_history.html'


class TwoFactorSetupView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/two_factor_setup.html'


class TwoFactorDisableView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/two_factor_disable.html'


class AccountDeleteView(LoginRequiredMixin, FormView):
    template_name = 'accounts/account_delete.html'
    form_class = AccountDeleteForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Hapus akun pengguna
        user = self.request.user
        user.delete()
        logout(self.request)
        return super().form_valid(form)