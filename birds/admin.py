from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Bird, Comment, Reply, Seed
# Register your models here.

class CommentInline(admin.TabularInline):
    model = Comment


class CustomAdminBird(admin.ModelAdmin):
    
    inlines = [
        CommentInline,
    ]
    
    list_display = ('species','location','picture','photographer','created',)


class ReplyInline(admin.TabularInline):
    model = Reply


class CustomAdminComment(admin.ModelAdmin):
    
    inlines = [
        ReplyInline,
    ]
    
    list_display = ('comment','bird','comment_creator', 'created',)



class CustomAdminSeed(admin.ModelAdmin):
    list_display = ('seeded','seeder','bird',)



admin.site.register(Bird, CustomAdminBird)
admin.site.register(Comment, CustomAdminComment)
admin.site.register(Seed, CustomAdminSeed)