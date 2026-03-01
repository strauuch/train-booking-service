from django.contrib import admin
from .models import Station, Route, TrainType, Train, Crew, Journey, Ticket, Order


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "latitude", "longitude")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "distance")


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "cargo_num",
        "places_in_cargo",
        "train_type",
        "capacity",
    )
    list_filter = ("train_type",)
    readonly_fields = ("capacity",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "full_name")
    readonly_fields = ("full_name",)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "train", "departure_time", "arrival_time")
    list_filter = ("route", "train")
    filter_horizontal = ("crew",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "journey", "cargo", "seat", "order")
    list_filter = ("journey",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_filter = ("user", "created_at")
