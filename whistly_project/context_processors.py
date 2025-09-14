from django.conf import settings


def site_settings(request):
    return {
        'adsense_client_id': getattr(settings, 'ADSENSE_CLIENT_ID', ''),
        'adsense_slot_top': getattr(settings, 'ADSENSE_SLOT_TOP', ''),
        'adsense_slot_inline': getattr(settings, 'ADSENSE_SLOT_INLINE', ''),
        'donation_url': getattr(settings, 'DONATION_URL', ''),
        'stripe_payment_link': getattr(settings, 'STRIPE_PAYMENT_LINK', ''),
        'nominatim_email': getattr(settings, 'NOMINATIM_EMAIL', ''),
        'hf_enabled': bool(getattr(settings, 'HF_API_TOKEN', '')),
    }
