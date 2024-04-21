# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import base64
import os
import pandas as pd
from openpyxl import load_workbook
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as Email, Attachment, FileContent, FileName, FileType, Disposition


def modifyPurchaseOrder(
    vendor_company_name,
    vendor_contact,
    vendor_address,
    vendor_city,
    item,
    description,
    qty,
    unit_price,
    total,
    ):
    workbook = load_workbook('purchase-order.xlsx')
    sheet = workbook.active
    sheet['A9'] = vendor_company_name
    sheet['A10'] = vendor_contact
    sheet['A11'] = vendor_address
    sheet['A12'] = vendor_city
    sheet['A20'] = item
    sheet['B20'] = description
    sheet['E20'] = qty
    sheet['F20'] = unit_price
    sheet['G20'] = total
    workbook.save('updated-purchase-order.xlsx')

def send_email(workbook_path):

    with open(workbook_path, 'rb') as f:

        data = f.read()
        encoded = base64.b64encode(data).decode()

        attachment = Attachment(
            file_content = FileContent(encoded),
            file_type = FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            file_name = FileName('purchase-order.xlsx'),
            disposition=Disposition('attachment')
        )
        message = Email(
            from_email='kate.yeh101@gmail.com',
            to_emails='kate.yeh101@gmail.com',
            subject='Sending with Twilio SendGrid is Fun',
            html_content='Thanks for handling our order. Please find purchase order attached.')

        message.attachment = attachment

        try:
            sg = SendGridAPIClient('API_KEY here')
            print(sg)
            response = sg.send(message)
            print(response)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)

send_email('purchase-order.xlsx')
