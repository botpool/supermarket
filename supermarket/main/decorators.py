from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def redirect_if_authenticated(view_func):
    decorated_view_func = user_passes_test(
        lambda user: not user.is_authenticated,
        login_url='/',
        redirect_field_name=None
    )(view_func)
    return decorated_view_func

def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return redirect('insufficient_permissions')
        return user_passes_test(lambda u: u.is_authenticated)(_wrapped_view)
    return decorator

def exclude_customer(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'customer':
            return redirect('insufficient_permissions')
        return view_func(request, *args, **kwargs)
    return user_passes_test(lambda u: u.is_authenticated)(_wrapped_view)
