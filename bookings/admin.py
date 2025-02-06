from django.contrib import admin
from .models import Seat, Booking, Ticket, Combo, ComboTicket
# Register your models here.
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(Ticket)
admin.site.register(Combo)
admin.site.register(ComboTicket)
