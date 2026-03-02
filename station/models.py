from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

User = get_user_model()


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="route_source"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="route_destination"
    )
    distance = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"], name="unique_route_source_destination"
            )
        ]

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    places_in_cargo = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="trains"
    )

    @property
    def capacity(self):
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journeys")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self):
        return f"{self.route} at {self.departure_time}"

    def clean(self):
        super().clean()
        if self.departure_time and self.arrival_time:
            if self.arrival_time <= self.departure_time:
                raise ValidationError(
                    {"arrival_time": "Arrival time must be after departure time."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["journey", "cargo", "seat"],
                name="unique_ticket_journey_cargo_seat",
            )
        ]
        ordering = ["id"]

    def __str__(self):
        return f"{self.journey}, Cargo: {self.cargo}, Seat: {self.seat}"

    @staticmethod
    def validate_ticket(
        cargo, seat, train_cargo_num, train_places_in_cargo, error_to_raise
    ):
        errors = {}

        if not (1 <= cargo <= train_cargo_num):
            errors["cargo"] = f"Cargo {cargo} is out of range"

        if not (1 <= seat <= train_places_in_cargo):
            errors["seat"] = f"Seat {seat} is out of range"

        if errors:
            raise error_to_raise(errors)

    def clean(self):

        if not self.journey_id:
            return
        train = self.journey.train
        if not train:
            return

        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train.cargo_num,
            self.journey.train.places_in_cargo,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)
