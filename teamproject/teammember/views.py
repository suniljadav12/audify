import os
from django.conf import settings
from django.http import HttpResponse,FileResponse
from django.shortcuts import redirect
from django.shortcuts import render
import youtube_dl
from moviepy.editor import VideoFileClip
from django.template.defaultfilters import slugify
import pyrebase
config = {

    'apiKey': "AIzaSyByu4NJ8sM7m0YEBxEkRFIvmvl1x_mB6lg",
    'authDomain': "video-to-audio-71cb2.firebaseapp.com",
    'databaseURL': "https://video-to-audio-71cb2-default-rtdb.firebaseio.com",
    'projectId': "video-to-audio-71cb2",
    'storageBucket': "video-to-audio-71cb2.appspot.com",
    'messagingSenderId': "138541334831",
    'appId': "1:138541334831:web:deef05723acba701e421da",

}
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()
storage = firebase.storage()
def signIn(request):
    return render(request,"Login.html")
 
def postsignIn(request):
    email = request.POST.get('email')
    pasw = request.POST.get('pass')
    try:
       
        user = authe.sign_in_with_email_and_password(email, pasw)
        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        return redirect("convert_video_to_audio")
    except:
        message = "Invalid Credentials!! Please check your data"
        return render(request, "Login.html", {"message": message})

def logout(request):
    try:
        del request.session['uid']
    except KeyError:
        pass
    return render(request, "Login.html")

def signUp(request):
    return render(request, "Registration.html")

def postsignUp(request):
    email = request.POST.get('email')
    passs = request.POST.get('pass')
    name = request.POST.get('name')
    try:
        
        user = authe.create_user_with_email_and_password(email, passs)
        uid = user['localId']
        return render(request, "Login.html")
    except:
        return render(request, "Registration.html")

def reset(request):
    return render(request, "Reset.html")

def postReset(request):
    email = request.POST.get('email')
    try:
        authe.send_password_reset_email(email)
        message = "An email to reset password is successfully sent"
        return render(request, "Reset.html", {"msg": message})
    except:
        message = "Something went wrong. Please check if the provided email is registered."
        return render(request, "Reset.html", {"msg": message})

def sanitize_filename(filename):
    
    return slugify(filename)


def convert_video_to_audio(request):
    if request.method == 'POST':
        if 'video' in request.FILES:
            # Video file upload
            video_file = request.FILES['video']

          
            if video_file.content_type.startswith('video/'):
                video_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
                audio_file = video_file.name.rsplit('.', 1)[0] + '.mp3'
                audio_path = os.path.join(settings.MEDIA_ROOT, audio_file)

               
                with open(video_path, 'wb') as f:
                    for chunk in video_file.chunks():
                        f.write(chunk)

                
                video = VideoFileClip(video_path)
                audio = video.audio
                audio.write_audiofile(audio_path)

               
                video.close()

                
                os.remove(video_path)

                
                storage_path = f"audio_files/{audio_file}"
                storage.child(storage_path).put(audio_path)

                
                download_url = storage.child(storage_path).get_url(None)

                
                database.child("audio_files").push(download_url)

                
                response = FileResponse(open(audio_path, 'rb'), content_type='audio/mpeg')
                response['Content-Disposition'] = f'attachment; filename="{audio_file}"'

                return response

        elif "youtube_link" in request.POST:
            
            youtube_link = request.POST.get('youtube_link')
            if youtube_link:
                try:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': os.path.join(settings.MEDIA_ROOT, 'youtube_video.mp4'),
                    }

                    
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(youtube_link, download=True)

                       
                        audio_file = "youtube_video.mp3"
                        audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_file)
                  
                    storage_path = f"audio_files/{audio_file}"
                    storage.child(storage_path).put(audio_file_path)

                    
                    download_url = storage.child(storage_path).get_url(None)

                    
                    database.child("audio_files").push(download_url)

                   
                    with open(audio_file_path, 'rb') as f:
                            response = HttpResponse(f.read(), content_type='audio/mpeg')
                            response['Content-Disposition'] = f'attachment; filename="{audio_file}"'
                            return response

                except Exception as e:
                    
                    error_message = f"Error extracting video: {str(e)}"
                    return HttpResponse(error_message, status=500)

   

        elif 'video_link' in request.POST:
               
                facebook_link = request.POST.get('video_link')
                if facebook_link:
                    try:
                        # Set the file paths and names
                        video_path = os.path.join(settings.MEDIA_ROOT, 'facebook_video.mp4')
                        audio_file = 'converted_audio.mp3'
                        audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_file)

                        # Download the Facebook video using youtube-dl
                        ydl_opts = {
                            'outtmpl': video_path,
                        }
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([facebook_link])

                        # Convert video to audio using moviepy
                        video = VideoFileClip(video_path)
                        audio = video.audio
                        audio.write_audiofile(audio_file_path)
                        video.close()
                        os.remove(video_path)

                        # Return the audio file as a response
                        storage_path = f"audio_files/{audio_file}"
                        storage.child(storage_path).put(audio_file_path)

                    # Get the download URL of the stored audio file
                        download_url = storage.child(storage_path).get_url(None)

                    # Save the audio file path in the Firebase Realtime Database
                        database.child("audio_files").push(download_url)

                    # Return the download URL as the response
                        with open(audio_file_path, 'rb') as f:
                            response = HttpResponse(f.read(), content_type='audio/mpeg')
                            response['Content-Disposition'] = f'attachment; filename="{audio_file}"'
                            return response
                        

                    except Exception as e:
                        # Handle any errors that occurred during the extraction
                        error_message = f"Error extracting video: {str(e)}"
                        return HttpResponse(error_message, status=500)
        elif 'twitch_link' in request.POST:
            # Video link from Twitch
            twitch_link = request.POST.get('twitch_link')
            if twitch_link:
                try:
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': os.path.join(settings.MEDIA_ROOT, 'twitch_video.mp4'),
                    }

                    # Download the audio file using youtube-dl
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(youtube_link, download=True)

                        # Get the sanitized file name
                        # sanitized_filename = sanitize_filename(info_dict['title'])
                        audio_file = "youtube_video.mp3"
                        audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_file)
                  # Store the audio file in Firebase Storage
                    storage_path = f"audio_files/{audio_file}"
                    storage.child(storage_path).put(audio_file_path)

                    # Get the download URL of the stored audio file
                    download_url = storage.child(storage_path).get_url(None)

                    # Save the audio file path in the Firebase Realtime Database
                    database.child("audio_files").push(download_url)

                    # Return the download URL as the response
                    with open(audio_file_path, 'rb') as f:
                            response = HttpResponse(f.read(), content_type='audio/mpeg')
                            response['Content-Disposition'] = f'attachment; filename="{audio_file}"'
                            return response

                except Exception as e:
                    # Handle any errors that occurred during the extraction
                    error_message = f"Error extracting video: {str(e)}"
                    return HttpResponse(error_message, status=500)



    return render(request, 'convert_video_to_audio.html')



def previous_conversions(request):
    conversions = []
    data = database.child("conversions").get()
    if data.each():
        for conversion in data.each():
            conversions.append(conversion.val())

    context = {
        "conversions": conversions
    }

    return render(request, "previous_conversions.html", context)