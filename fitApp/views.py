from django.shortcuts import render

def home(request):
    return render(request, 'homescreen.html')

def analyzing(request):
    if request.method == 'POST':
        # Printing what was uploaded for now for storage.
        print("Received:", request.FILES.get('user_image'), request.FILES.get('athlete_image'))
        return render(request, 'homescreen.html') # Keeping it on the same page for now

    return render(request, 'homescreen.html')