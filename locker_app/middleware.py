from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    # Store user identity in the signed session cookie on login
    request.session['user_email'] = user.email
    request.session['user_username'] = user.username

class ServerlessSessionMiddleware:
    """
    Middleware to handle serverless ephemeral SQLite DB recreation.
    If a different Vercel lambda instance handles the request and doesn't find the user
    in its local SQLite database, this middleware recreates the user on the fly using
    data stored in the signed cookie session, restoring their logged-in state seamlessly.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and not request.user.is_authenticated:
            user_email = request.session.get('user_email')
            user_username = request.session.get('user_username')
            if user_email and user_username:
                try:
                    # Get or recreate the user in this lambda instance's local db
                    user, created = User.objects.get_or_create(
                        email=user_email,
                        defaults={'username': user_username}
                    )
                    if created:
                        user.set_unusable_password()
                        user.save()
                    
                    # Re-login the user for this request
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                except Exception as e:
                    # Fail silently to avoid breaking the request
                    print(f"Error in ServerlessSessionMiddleware: {e}")
                    
        return self.get_response(request)
