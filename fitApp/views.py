from django.shortcuts import render
from django.core.files.storage import default_storage
from .estimator import analyze_pose
import os
from django.conf import settings
from PIL import Image
import io
import uuid


def home(request):
    return render(request, 'homescreen.html')

def analyzing(request):
    if request.method == 'POST':
        user_image = request.FILES.get('user_image')
        athlete_image = request.FILES.get('athlete_image')

        if not user_image or not athlete_image:
            print("Missing user or athlete image.")
            return render(request, 'homescreen.html', {
                'error': 'Please upload both images for analysis.'
            })

        user_path = default_storage.save('tmp/user_image.jpg', user_image)
        athlete_path = default_storage.save('tmp/athlete_image.jpg', athlete_image)

        abs_user_path = os.path.join(settings.MEDIA_ROOT, user_path)
        abs_athlete_path = os.path.join(settings.MEDIA_ROOT, athlete_path)

        print(f"Absolute user image path: {abs_user_path}")
        print(f"Absolute athlete image path: {abs_athlete_path}")

        try:
            # --- Pre-analysis test cases ---
            if os.path.exists(abs_user_path) and os.path.exists(abs_athlete_path):
                print("Uploaded image files exist.")
            else:
                raise FileNotFoundError("One or both image files were not saved correctly.")

            angle_differences, overlay1, overlay2 = analyze_pose(abs_user_path, abs_athlete_path)

            print(f"Angle differences found for {len(angle_differences)} joints:")
            for joint, angle in angle_differences.items():
                print(f"   - {joint}: {angle:.2f}°" if angle is not None else f"   - {joint}: Not detected")

            # Save overlay images
            overlay1_io = io.BytesIO()
            overlay2_io = io.BytesIO()
            Image.fromarray(overlay1).save(overlay1_io, format='JPEG')
            Image.fromarray(overlay2).save(overlay2_io, format='JPEG')

            uid = str(uuid.uuid4())
            overlay1_path = f'tmp/overlay_user_{uid}.jpg'
            overlay2_path = f'tmp/overlay_athlete_{uid}.jpg'

            default_storage.save(overlay1_path, overlay1_io)
            default_storage.save(overlay2_path, overlay2_io)

            print("Overlay images saved successfully.")

        except Exception as e:
            print(f" Exception during analysis: {str(e)}")
            return render(request, 'homescreen.html', {
                'error': f"Something went wrong: {str(e)}"
            })
        return render(request, 'results.html', {
            'angle_differences': angle_differences,
            'user_image_url': default_storage.url(overlay1_path),
            'athlete_image_url': default_storage.url(overlay2_path),
        })


    return render(request, 'homescreen.html')