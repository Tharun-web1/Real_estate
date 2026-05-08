from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_referral_code','username', 'email', 'phone', 'role', 'plan_type', 'click', 'leads')
    search_fields = ('username', 'email', 'phone', 'company_name')
    list_filter = ('role', 'plan_type', 'created_at')

@admin.register(AddPropertyModel)
class AddPropertyModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'projectName', 'selectProperty', 'user', 'is_verified', 'image', 'video', 'document')
    search_fields = ('projectName', 'selectProperty', 'user__username')
    list_filter = ('selectProperty', 'is_verified', 'look')
    
# franchis form
@admin.register(FranchiseApplication)
class FranchiseApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "contact", "location", "submitted_at")
    search_fields = ("full_name", "email", "location")
    
# my requremnt form
@admin.register(FutureRequirement)
class FutureRequirementAdmin(admin.ModelAdmin):
    list_display = (
        "property_type",
        "city",
        "state",
        "budget",
        "location",
    )
    list_filter = ("city", "state", "approval_type")
    search_fields = (
        "property_type",
        "city",
        "state",
        "budget",
        "project_name",
        "company_name",
    )


admin.site.register(MoveRequest)
admin.site.register(ContactForm)
admin.site.register(LoanApplication)
admin.site.register(AddProject)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "requirement", "message", "cid", "user", "created_at")
    search_fields = ("name", "email", "requirement", "message", "cid")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


admin.site.register(Reels)
admin.site.register(Comment)


admin.site.register(ProfileLeadsModel)
admin.site.register(PropertyLeadsModel)
admin.site.register(ProjectLeadsModel)





from django.contrib import admin
from .models import ChatRoom, ChatMessage

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')  # updated fields
    list_filter = ('created_at',)
    search_fields = ('user1__username', 'user2__username')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'message')

from .models import PostFeed, ImagePost

@admin.register(PostFeed)
class PostFeedAdmin(admin.ModelAdmin):
    list_display = ('media_type', 'created_at')


@admin.register(ImagePost)
class ImagePostAdmin(admin.ModelAdmin):
    list_display = ('heading', 'created_at')

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('heading', 'user', 'created_at')
    search_fields = ('heading', 'news_content')

@admin.register(NewsKeyword)
class NewsKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'created_at')
    search_fields = ('keyword',)