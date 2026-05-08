from django.urls import path,include
from . import views
from django.contrib.auth.views import LogoutView 
from django.http import JsonResponse
import json
from django.conf import settings
import os

def assetlinks(request):
    file_path = os.path.join(settings.BASE_DIR, 'static/.well-known/assetlinks.json')
    with open(file_path) as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)

app_name = 'prop'

urlpatterns = [
    path('.well-known/assetlinks.json', assetlinks),
    path("login/register", views.register_user, name="register"),
    path("register/step1/", views.register_step1_ajax, name="register_step1_ajax"),
    path("register/step2/", views.register_step2_ajax, name="register_step2_ajax"),
    path("register/subscribe/", views.register_subscribe, name="register_subscribe"),
    path("login/", views.login_user, name="login"),
    path('register_choice/', views.register_choice, name='register_choice'),
    path('logout/', LogoutView.as_view(next_page='/login/'),name='logout'),
    path('', views.home, name='home'),
    path('add-property/', views.add_property, name='add_property'),
    # path('properties/', views.property_list, name='property_list'),
    #profile page


    path('search/',views.search, name= 'search'),

    
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),

    path('all-users/', views.all_users, name="all_users"),

    path('properties/<str:prop>/', views.property_list, name='property_list'),
    path("get-property/<str:prop>/", views.get_Property, name="get_property_type"),
    path('property/<int:id>/', views.property_detail, name='property_detail'),
    
    # franchise in home
    
    path("franchise/",views.franchise,name= "franchise"),
    path("franchise-register/", views.franchise_register, name="franchise_register"),
    path("franchise-profile/", views.franchise_profile, name="franchise_profile"),
    path("franchise-edit/", views.franchise_edit, name="franchise_edit"),
    path("verify-property/", views.verify_property, name="verify_property"),
    path("verify-property/<int:property_id>/", views.verify_property, name="verify_property_with_id"),
    #my requremt form
    path('require/', views.requirement_form, name="require"),

    path('profile/', views.profile , name='profile'),
    path("professional/profile/", views.professional_profile_view, name="professional_profile"),
    path("professional/profile/<int:user_id>/", views.professional_profile_view, name="professional_profile_with_id"),
    path("marketer/profile/", views.marketer_profile_view, name="marketer_profile"),
    path("marketer/profile/<int:user_id>/", views.marketer_profile_view, name="marketer_profile_with_id"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('user_uploades/',views.user_uploades, name='user_uploades'),
    path('referral/', views.referral, name='referral'),
    path('loan-form/', views.loan_form, name='loan_form'),

    path("contact/", views.contact_form_view, name="contact_form"),
    path("move-form/", views.move_form, name="move_form"),
    

    path("company-register/", views.company_register, name="company_register"),
    # path("franchise-register/", views.franchise_register, name="franchise_register"),
    path("addproject/", views.add_project, name='add_project'),

    path("project/<int:id>/", views.project_detail, name="project_detail"),
    path("all-projects/", views.all_projects, name="all_projects"),
    path("projects_views_list/",views.projects_views_list, name='projects_views_list'),
    path("projects_views_list/<int:user_id>/", views.projects_views_list, name="projects_views_list_with_id"),

    path("property_leads_get/<int:id>",views.property_leads_get,name="property_leads_get"),


    path("saved/", views.saved_properties, name="saved_properties"),
    path("save-project/<int:project_id>/", views.save_project, name="save_project"),
    path("save/<int:property_id>/", views.save_property, name="save_property"),



        # >>> Company profile (corrected, accepts user ID)
    path("company/profile/", views.company_profile_view, name="company_profile"),
    path("company/profile/<int:user_id>/", views.company_profile_view, name="company_profile_with_id"),


    # Contact
    path("contact-submit/", views.contact_submit, name="contact_submit"),


    path("otp/send/", views.send_otp, name="send-otp"),
    path("otp/verify/", views.verify_otp, name="verify-otp"),
    path("story/mark-seen/<int:post_id>/", views.mark_story_seen, name="mark_story_seen"),


    path("project/delete/<int:id>/", views.delete_project, name="delete_project"),
    path("project/sold/<int:id>/", views.mark_sold, name="mark_sold"),
    path("project/edit/<int:id>/", views.edit_project, name="edit_project"),
    path("reel/delete/<int:id>/", views.delete_reel, name="delete_reel"),


    path("reelUpload",views.reels_upload,name='reelUpload'),
    path('getReel',views.get_reel,name='getReel'),
    path('likeReel/<int:id>',views.like_reel,name='likeReel'),
    path('comment/<int:id>/<str:comment>',views.comment_reel,name='commentReel'),
    path('getAllComments/<int:id>',views.getAllComments,name='getAllComments'),
    path('reel/view/<int:reel_id>/', views.register_reel_view, name='register_reel_view'),
    path('reels/', views.reel_viewer, name='all_reels'),
    path('delete-reel/<int:id>/', views.delete_reel, name='deleteReel'),
    path("reel/edit/<int:id>/", views.edit_reel, name="edit_reel"),

    path("terms/", views.terms_and_conditions, name="terms"),
    path('forgetPass/',views.forget_password,name='forgetPass'         ),
    path("reset-password", views.reset_password, name="reset_password"),
    path("pass/send-otp/", views.send_otp_pass, name="send_otp_pass"),
    path("pass/verify-otp/", views.verify_otp_pass, name="verify_otp_pass"),
    path("delete/<int:id>/", views.delete_property, name="delete_property"),
    path('sold/<int:id>/', views.make_sold, name='make_sold'),
    
    #leads
    path('profilellead/<int:id>/',views.profilelead_view,name='profilellead'),
    path('projectlead/<int:id>/<int:proId>/',views.projectlead_view ,name='projectllead'),
  # path('propertyllead/<int:id>/<int:propId>',views.propertlead_view ,name='propertyllead'),
    path('propertyllead/<int:id>/<int:propId>/', views.propertlead_view, name='propertyllead'),
    
    path("filterbox/", views.filterbox, name="filterbox"),
    path("leads/", views.leads_page, name="leads_page"),
       path("property-leads/<int:id>/", views.property_leads_page, name="property_leads_page"),
       path("company/<int:user_id>/leads/", views.company_leads_page, name="company_leads_page"),
    path("project/<int:project_id>/leads/", views.project_leads_page, name="project_leads"),
 path("get_property/<int:id>/", views.get_property_details, name="get_property"),
 path("edit_property/<int:id>/", views.edit_property, name="edit_property"),
 
 
 
    path("users/", views.all_users_to_chat, name="all_users_to_chat"),
    path("start/<int:user_id>/", views.start_chat_with_user, name="start_chat_with_user"),
    path("<int:chat_id>/", views.chat_room, name="chat_room"),
    path("notifications/api/count/", views.new_messages_count, name="new_messages_count"),
     path(
        "chat/property/<int:property_id>/",
        views.start_property_chat,
        name="start_property_chat",
    ),
  path(
    'owner/property/chats/',
    views.owner_property_chats,
    name='owner_property_chats'
),


    path("renew-plan/", views.renew_plan, name="renew_plan"),
    path("select-plan/", views.select_plan, name="select_plan"),


# admin urls
path('all-project/', views.all_project, name='all_project'),
 


   path("contacts/", views.all_contacts, name="all_contacts"), 
   path("all-requests/", views.all_requests, name="all_requests"),
  path("update-plans/", views.update_plans, name="update_plans"),
  
path("admin-properties/", views.admin_properties, name="admin_properties"),
path("toggle-verify/<int:pk>/", views.toggle_verify_property, name="toggle_verify_property"),
path('toggle-illegal/<int:pk>/', views.toggle_illegal_property, name='toggle_illegal_property'),

# prop/urls.py
path('properties-verification/', views.property_verification_list, name='properties_verification'),
path("futureRequirement/",views.FutureRequire,name="futureRequirement"),
path("franchise-list/", views.franchies_list, name="franchise_list"),
path("property/stats/", views.property_stats, name="property_stats"),
path('marketing/renew/', views.marketing_renew_plans, name='marketing_renew_plan'),  
path("property/check-details/<int:property_id>/", views.check_property_details, name="check_property_details"),

    path("create-order/", views.create_order, name="create_order"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    
    
    path("manage-slides/", views.manage_slides, name="manage_slides"),
    path("delete-slide/<int:id>/", views.delete_slide, name="delete_slide"),
    path("admin-owner-properties/", views.owner_properties, name="owner_properties"),
    path('toggle-rera/<int:pk>/', views.toggle_rera_property, name='toggle_rera_property'),
    
    path('careers/', views.careers, name='careers'),
    path('about-us/', views.about_us, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact-us/', views.contact, name='contact'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('help/', views.help_view, name='help'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/edit/<int:pk>/', views.news_edit, name='news_edit'),
    path('news/delete/<int:pk>/', views.news_delete, name='news_delete'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),

    # Feed
    path('feed/', views.feed_list, name='feed_list'),
    path('feed/create/', views.feed_create, name='feed_create'),
    path('feed/edit/<int:pk>/', views.feed_edit, name='feed_edit'),
    path('feed/delete/<int:pk>/', views.feed_delete, name='feed_delete'),
    path('feed/<int:pk>/', views.feed_detail, name='feed_detail'),


    path('profiless/', views.profile_pagess, name='profiless'),


 
path('poll/create/', views.poll_create, name='poll_create'),
path('poll/vote/<int:pk>/', views.poll_vote, name='poll_vote'),
path('poll/delete/<int:pk>/', views.poll_delete, name='poll_delete'),
path('notifications/', views.notifications_list, name='notifications_list'),
path('mark-notifications-read/', views.mark_all_notifications_read, name='mark_notifications_read'),
path('settings/', views.settings_view, name='settings'),
]