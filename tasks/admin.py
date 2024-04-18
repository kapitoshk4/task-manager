from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.models import (
    Task,
    Position,
    TaskType,
    Worker,
    Project
)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "deadline", "status", ]
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
    list_display = ["name", "description", "creator", ]
    search_fields = ["name", ]


admin.site.register(Position)
admin.site.register(TaskType)
