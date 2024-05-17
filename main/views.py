from django.shortcuts import render, redirect
from lib_database.query import *
from lib_database.user import *
import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import uuid

# Create your views here.
def show_main(request):
    return render(request, "main.html")

@csrf_exempt
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        data = search_user(email, password)
        if len(data) != 0:

            user = authenticate(username=email,email=email, password=password)
            if user is not None:
                login(request, user)
            else : 
                user = User.objects.create_user(email=email, password=password, username=email)
                user.save()
                login(request, user)
            return HttpResponseRedirect(reverse('main:index'))
        
        else :
            data = search_label(email, password)
            if len(data) != 0:
                uu_id = get_user_uu_id(email)
                user = authenticate(username=uu_id,email=email, password=password)
                if user is not None:
                    login(request, user)
                else : 
                    uu_id = get_user_uu_id(email)
                    user = User.objects.create_user(email=email, password=password, username=uu_id)
                    user.save()
                    login(request, user)
                return HttpResponseRedirect(reverse('main:index'))
            else:
                messages.info(request, 'Email or password is incorrect')
                return render(request, "login.html")
                
    return render(request, "login.html")

def index(request):
    email = request.user.email
    role = get_user_type(email)
    if role == "Label":
        data = get_data_label(email)
        return render(request, "index_label.html", {'id': data[0][0], 'nama': data[0][1], 'email': data[0][2], 'kontak': data[0][4]})
    else:
        return redirect('main:homepage')

def register_option(request):
    return render(request, "register_base.html")

def register_user(request):
    return render(request, "register_pengguna.html")
@csrf_exempt
def register_label(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        nama = request.POST.get("nama")
        kontak = request.POST.get("kontak")
        data = search_label(email, password)
        if len(data) != 0:
            messages.info(request, 'Email already registered')
            return render(request, "register_label.html")
        else:
            uu_id = str(uuid.uuid4())
            id_pemilik_hak_cipta = str(uuid.uuid4())
            insert_label(uu_id, nama, email, password, kontak,id_pemilik_hak_cipta)
            user = User.objects.create_user(email=email, password=password, username=uu_id)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('main:index_label'))
    return render(request, "register_label.html")

def royalty_list(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login first')
        return redirect('main:user_login')
    email = request.user.email
    royalty_list = get_royalty_list(email)
    name = get_user_name(email)
    return render(request, "royalty_list.html", {'royalty_list': royalty_list, 'name': name})

def album_list(request):
    email = request.user.email
    index = request.user.username
    role = get_user_type(email)
    if role == "Label":
        name = get_label_name(email)
    else :
        name = get_user_name(email)
    if role == "Label":
        album_list = get_album_list_label(index)
        return render(request, "album_list_label.html", {'album_list': album_list, 'name': name})
    if role == "Artist":
        album_list = get_album_list_artist(index)
        return render(request, "album_list_artist.html", {'album_list': album_list, 'name': name})
    if role == "Songwriter":
        album_list = get_album_list_songwriter(index)
        return render(request, "album_list_songwriter.html", {'album_list': album_list, 'name': name})
    
@csrf_exempt
def homepage(request):
    account = get_account(request.user.email)
    gender = "" 
    if account[0][3] == 0:
        gender = "Perempuan"
    else:
        gender = "Laki-laki"
    context = {
        "email": account[0][0],
        "username": account[0][2],
        "gender": gender,
        "tempat_lahir": account[0][4],
        "tanggal_lahir": account[0][5],
        "kota_asal": account[0][7],
        "subscription": request.COOKIES.get("subscription")
    }
    return render(request, "index.html", context)

def logout(request):
    response = HttpResponseRedirect(reverse('main:show_main'))
    response.delete_cookie('email')
    response.delete_cookie('subscription')
    return response

def album_detail(request, album_name):
    song_list = get_song_album(album_name)
    if "'" in album_name:
        album_name = album_name.replace("'", "''")
    return render(request, "album_list_song.html", {'song_list': song_list, 'album_name': album_name})

def delete_album(request, album_name):
    if "'" in album_name:
        album_name = album_name.replace("'", "''")
        
    delete_album_by_name(album_name)
    return redirect('main:album_list')

def delete_song(request, song_name):
    if "'" in song_name:
        song_name = song_name.replace("'", "''")
    delete_song_by_name(song_name)
    return redirect('main:album_list')

def song_detail(request, song_name):
    if "'" in song_name:
        song_name = song_name.replace("'", "''")
    song_detail = get_song_detail(song_name)
    return render(request, "song_detail.html", {'song_detail': song_detail})
   
def create_album(request):
    if request.method == "POST":
        album_id = str(uuid.uuid4())
        album_name = request.POST.get("album-name")
        album_label = request.POST.get("album-label")
        album_label_id = get_label_uuid_by_name(album_label)
        jumlah_lagu = 0
        total_durasi = 0
        insert_album(album_id, album_name, jumlah_lagu, album_label_id, total_durasi)
        return redirect('main:album_list')
    label_list = get_label_list()
    return render(request, "create_album.html", {'label_list': label_list})

def create_song_songwriter(request, album_name):
    songwriter_name = get_songwriter_name(request.user.username)
    artist_list = get_artist_list()
    genres = [
    "Pop",
    "Rock",
    "Hip-hop/Rap",
    "Country",
    "Jazz",
    "Blues",
    "Electronic/Dance",
    "R&B (Rhythm and Blues)",
    "Reggae",
    "Folk",
    "Indie",
    "Metal",
    "Punk",
    "Classical",
    "Latin",
    "World",
    "Funk",
    "Gospel",
    "Ambient",
    "Experimental"
]
    if request.method == "POST":
        song_id = str(uuid.uuid4())
        album_name = request.POST.get("album-name")
        song_name = request.POST.get("song-name")
        song_artist_id = request.POST.get("song-artist")
        song_writer = request.POST.get("song-writer")
        song_genre = request.POST.getlist("song-genre")
        song_duration = request.POST.get("song-duration")
        add_song_songwriter(song_id, song_name, song_artist_id, song_writer, song_genre, song_duration, album_name)
        return redirect('main:album_list')
    return render(request, "create_song_songwriter.html", {'album_name': album_name, 'songwriter_name': songwriter_name, 'artist_list': artist_list, 'genres': genres})

def create_song_artist(request, album_name):
    artist_name = get_artist_name(request.user.username)
    songwriter_list = get_songwriter_list()
    genres = [
    "Pop",
    "Rock",
    "Hip-hop/Rap",
    "Country",
    "Jazz",
    "Blues",
    "Electronic/Dance",
    "R&B (Rhythm and Blues)",
    "Reggae",
    "Folk",
    "Indie",
    "Metal",
    "Punk",
    "Classical",
    "Latin",
    "World",
    "Funk",
    "Gospel",
    "Ambient",
    "Experimental"
]
    if request.method == "POST":
        song_id = str(uuid.uuid4())
        album_name = request.POST.get("album-name")
        song_name = request.POST.get("song-name")
        song_artist_name = request.POST.get("song-artist")
        song_artist_id = get_artist_id_by_name(song_artist_name)
        song_writers = request.POST.getlist("song-writer")
        song_genres = request.POST.getlist("song-genre")
        song_duration = request.POST.get("song-duration")
        add_song_artist(song_id, song_name, song_artist_id, song_writers, song_genres, song_duration, album_name)
        return redirect('main:album_list')
    return render(request, "create_song_artist.html", {'album_name': album_name, 'artist_name': artist_name, 'genres': genres, 'songwriter_list': songwriter_list})