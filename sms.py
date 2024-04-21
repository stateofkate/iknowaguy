from twilio.rest import Client

account_sid = 'ACa8130ad26f12176f7a7865bd32b64c92'
auth_token = '[AuthToken]'
client = Client(account_sid, auth_token)


def create_sms_body(
        vendors_contacted,
        sku,
        vendor,
        price,
        qty,
        date,
):
    return f"We called {vendors_contacted} vendors. This is the best order we found: \nSKU: {sku}\nPrice: {price}\nShip by: {date}. Would you like to place the order?"


def send_sms(sms_body):
    message = client.messages.create(
    from='+18666061424',
    body='hello',
    to='+19292806660'
    )

    print(message.sid)


#create sms body
# pass to send_sms
