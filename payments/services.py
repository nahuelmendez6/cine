from datetime import timedelta
from django.utils.timezone import now
from payments.models import Promotion

def apply_discounts(booking, payment_info):
    """
    Aplica descuentos a la reserva según promociones activas
    """
    total_price = booking.total_price # tomamos el precio original de la reserva
    applicable_promotions = Promotion.objects.filter(active=True) # filtramos las promociones activas

    for promo in applicable_promotions:
        # 1. Descuento por día de la semana (ej: 2x1 los miercoles)
        if promo.applicable_day and booking.function.function_date.strftime('%A') == promo.applicable_day:
            if promo.discount_type == '2x1' and booking.tickets.count() >= 2:
                total_price -= booking.function.price

        # 2. Descuento por tipo de tarjeta
        if promo.card_type and promo.card_type == payment_info.get('card_type'):
            if promo.discount_type == 'percentage':
                total_price -= total_price * (promo.discount_value / 100)

        # 3. Descuento por compra anticipada
        if promo.days_before_function:
            days_before = (booking.function.function_date - now().date()).days
            if days_before >= promo.days_before_function:
                if promo.discount_type == 'percentage':
                    total_price -= total_price * (promo.discount_value / 100)

        # 4. Ofertas por cantidad de entradas compradas
        if promo.min_tickets and booking.tickets.count() >= promo.min_tickets:
            if promo.discount_type == 'percentage':
                total_price -= total_price * (promo.discount_value / 100)

        return max(total_price, 0)