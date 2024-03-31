from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib.auth import logout

CustomUser = get_user_model()


def index(request):
    try:
        user_id = request.session.get('user_id')

        if user_id:
            # Get the user based on their ID
            user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist as e:
        print("User does not exist:", e)
    except Exception as e:
        print("An error occurred:", e)

    return render(request, 'index.html', {"user": user})


def upload_view(request):
    return None


