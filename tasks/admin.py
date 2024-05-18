from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.models import (
    Task,
    Position,
    TaskType,
    Worker,
    Project, TaskComment
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "deadline", "status", "creator", "project", ]
    list_filter = ["deadline", "status"]
    search_fields = ["name", ]


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position", )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "position",
                    )
                },
            ),
        )
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "creator", ]
    search_fields = ["title", ]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ["message", "sender", "task",]


admin.site.register(Position)
admin.site.register(TaskType)
