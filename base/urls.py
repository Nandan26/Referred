from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    
    path('room/<str:room_id>/',views.room, name= 'room'),
    
    path('create-room/',views.create_room, name = 'create-room'),
    path('update-room/<str:room_id>/',views.update_room, name = 'update-room'),
    path('delete-room/<str:room_id>/',views.delete_room, name = 'delete-room'),
    path('room-details/<str:room_id>/',views.room_details, name = 'room-details'),
    
    path('login/',views.login_page, name = 'login'),
    path('logout/',views.logout_page, name = 'logout'),
    path('register/',views.register_page, name = 'register'),

    path('delete-msg/<str:msg_id>/',views.delete_message, name = 'delete-msg'),
    path('profile/<str:user_id>/', views.user_profile, name = 'user-profile'),
    
    path('update-user/',views.update_profile, name = 'update-user'),
    path('comps/', views.comp_page, name = 'comps'),
    path('activity-page/', views.activity_page, name = 'activityPage'),
    path('activity/<str:user_id>', views.user_activity, name = 'user-activity'),
    path('following/', views.following, name = 'following'),

    path('profile/<str:recruiter_id>/followers/add', views.add_follower, name='add-follower'),
    path('profile/<str:recruiter_id>/followers/remove', views.remove_follower, name='remove-follower'),
    path('notifications/<str:not_id>', views.view_notifications, name = 'del-notification'),

    path('room/<str:room_id>/apply/', views.apply_now , name = 'apply'),
    path('application/<str:application_id>', views.update_application, name='update-application'),

    path('applications/', views.my_applications, name = 'myApplications'),
    path('room/<str:room_id>/applications/', views.view_applications, name = 'applications'),
    path('room/<job_id>/select-application/<can_id>/', views.select_application, name='select-application'),
    path('room/reject-application/<application_id>/', views.reject_application, name = 'reject-application'),
]
