import telebot
import json
import random
import string
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging
import re
import httpx
import asyncio
from telebot import types
from bs4 import BeautifulSoup

namebot = 'ERROR'
token = '7813481159:AAGQaTvB-NJkZitqtkv7Gip8lVE5t0EAsnM'
bot = telebot.TeleBot(token)

admin = 7253621444

logging.basicConfig(level=logging.INFO)

stop_scanning = False
allow_scanning = False

async def fetch_url(url, retries=3, delay=5):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()  # Raise an error for bad responses
                return response.text
        except httpx.RequestError as e:
            logging.error(f"Request error occurred: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")
            break  # Exit on HTTP errors
    return None

async def check_payment_gateway_async(url):
    payment_methods = []
    
    content = await fetch_url(url)
    if content is None:
        logging.error(f"Failed to fetch content from {url}")
        return payment_methods

    soup = BeautifulSoup(content, 'html.parser')
    gateways = [
                r'Stripe', r'Bolt', r'Stripe 2D', r'PayPal', r'Braintree', r'ProPay', 
    r'Payoneer', r'Cash on Delivery (COD)', r'PayFast', r'Fattura24', r'PayU', r'Paytm', 
    r'Adyen', r'AWS', r'Checkout', r'StormPay', r'PayIt', r'Xoom', 
    r'Zelle', r'Authorize Net CIM', r'Klarna', r'Facebook Pay', r'Cashless', 
    r'Bokun', r'Pay2Go', r'Authorize.Net', r'PayMate', r'AuthorizeNet', 
    r'Authorize Net CIM ECheck', r'Viva Wallet', r'Payment Vision', 
    r'SecurionPay', r'PayCentral', r'Transaction', r'CBA', 
    r'Payment Express', r'Verified by Visa', r'Pagar.me', r'PayLane', 
    r'NetSpend', r'Paxum', r'WorldPay', r'BitPay', r'Cash on Delivery (COD)', 
    r'Payouts', r'Wirecard', r'P2P', r'PaySend', r'WeChat Pay', 
    r'Merchant Warrior', r'Trustly', r'CurrencyFair', r'CPay', 
    r'Xendit', r'Venmo', r'Apple Pay', r'Google Wallet', r'Cash App', 
    r'PayForIt', r'Bill.com', r'Eway Rapid', r'Eway', r'PaymentLink', 
    r'DirectPay', r'PayPal Here', r'Paymentus', r'Forte Payment Systems', 
    r'SecurePay', r'PandaPay', r'Pivotal Payments', r'Payza', 
    r'Authorize\.Net', r'Square', r'2Checkout', r'Mollie', 
    r'Razorpay', r'WePay', r'Skrill', r'Alipay', r'Chase', 
    r'Amazon Pay', r'Dwolla', r'Checkout\.com', r'BlueSnap', 
    r'Ecommerce Gateway', r'Revolut', r'Nexi', r'SumUp', 
    r'Paylike', r'Eway Rapid', r'Cash on Delivery \(COD\)', 
    r'ANZ', r'PayPal Good', r'AVS', r'NAB', r'WooCommerce', 
    r'CashApp', r'QuickBooks', r'PaymentSpring', r'Serve', 
    r'Bitcoin', r'Coinbase Commerce', r'SoftPay', r'Square Cash', 
    r'Gumroad', r'Paysera', r'PayU India', r'Paytm Wallet', 
    r'GoCardless', r'Sezzle', r'Afterpay', r'Laybuy', 
    r'Openpay', r'Splitit', r'Paymentwall', r'Flexepin', 
    r'Paysafe', r'Boku', r'Interswitch', r'Flutterwave', 
    r'Paystack', r'Cashfree', r'Payfort', r'Paddle', 
    r'3D Secure', r'Neteller', r'Sofort', r'Giropay', 
    r'Ideal', r'KBC', r'Bancontact', r'Payconiq', 
    r'Kashier', r'Airwallex', r'TransferWise', r'Wise', 
    r'Apple Cash', r'cash on delivery (cod)', r'CASH ON DELIVERY (COD)', 
    r'Cash On Delivery (Cod)', r'cAsH On dElIvErY (cOd)', 
    r'CaSH ON DeLiVeRY (COD)', r'cash ON delivery (COD)', 
    r'CAsH oN dElIvErY (cOd)', r'BillDesk', r'PaymentCloud', r'Settle', 
    r'CoinPayments', r'FastSpring', r'Clearpay', r'Zip', 
    r'Aftapay', r'Quickpay', r'EasyPay', r'PayPoint', 
    r'Hyperwallet', r'PayByPhone', r'Kabbage', r'Affirm', 
    r'Transaction', r'Cash On Delivery (COD)', r'Billplz', r'Paydollar', r'Omise', 
    r'PayTabs', r'PayLike', r'MPesa', r'Zapper', 
    r'Sowingo', r'Paga', r'Rpay', r'PaySense', 
    r'AirPay', r'RaiPay', r'Paygates', r'Rapid', 
    r'Invoice', r'Tinkoff', r'Paylum', r'xendit', 
    r'PayLane', r'Infinix', r'GoPayment', r'SoftBank', 
    r'P2P', r'PaySend', r'TransferGo', r'WorldRemit', 
    r'SettlePay', r'Gocardless', r'Payoneer', r'Pivotal Payments', 
    r'Payza', r'CBA', r'cash on delivery (cod)', r'Epay', r'Moneybookers', r'Riyad Bank', 
    r'SamaPay', r'ZainCash', r'PayPal Plus', r'CashNet', 
    r'MyBank', r'Payza', r'SoftPay', r'Paga', r'Payfort', 
    r'Airwallex', r'Fattura24', r'Pivotal Payments', r'PandaPay', 
    r'ZainCash', r'Riyad Bank', r'Venmo', r'Kashier', 
    r'Cashfree', r'PayMate', r'CashNet', r'BillDesk', 
    r'Boku', r'Payouts', r'GoCardless', r'Xendit', 
    r'P2P', r'PayLike', r'PayU India', r'CBA', 
    r'CoinPayments', r'SecurePay', r'Forte Payment Systems', 
    r'PaymentSpring', r'Hyperwallet', r'Afterpay', r'PayByPhone', 
    r'Clearpay', r'SettlePay', r'Braintree', r'BitPay', 
    r'Checkout.com', r'Flexepin', r'Ideal', r'Payconiq', 
    r'3D Secure', r'Pivotal Payments', r'PaymentLink', 
    r'Zapper', r'WeChat Pay', r'PaySend', r'Paymentus', 
    r'Xendpay', r'Cashu', r'GPay', r'Affirm', 
    r'AliExpress', r'Allied Wallet', r'Allpay', r'American Express', 
    r'Android Pay', r'Apple Card', r'Asiapay', r'Atome', 
    r'Baloto', r'BitGold', r'Blackhawk Network', r'Blik', 
    r'Bluedart', r'Braspag', r'Business World', r'CCBill', 
    r'Cellum', r'Chase Pay', r'Chip and PIN', r'Circle', 
    r'Citcon', r'ClearBank', r'ClickandBuy', r'Conekta', 
    r'Converge', r'Corepay', r'Creditcall', r'CryptoPay', 
    r'Cubits', r'DLocal', r'Dash', r'Decentro', 
    r'Diners Club', r'Discover', r'Dwolla', r'ECOBANQ', 
    r'Ecommpay', r'Elavon', r'Embily', r'Enstream', 
    r'Epro', r'Escher', r'Euronet', r'Eximbay', 
    r'Ezidebit', r'FairPlayPay', r'Fastcash', r'Finix', 
    r'Fiserv', r'FONDY', r'Freecharge', r'G2A Pay', 
    r'Galileo', r'Gateway.io', r'GCash', r'GlobalCollect', 
    r'Google Pay', r'Green Dot', r'Halcash', r'Handpoint', 
    r'Hemel', r'Hipay', r'HooYu', r'HSBC', 
    r'Huawei Pay', r'HyperPay', r'IDEAL', r'INPAY', 
    r'InstaPay', r'Interac', r'JCB', r'JetPay', 
    r'JumiaPay', r'Klarna', r'Knet', r'Komoju', 
    r'KPay', r'KueskiPay', r'LianLian Pay', r'Line Pay', 
    r'Linkly', r'Marqeta', r'Mastercard', r'MB Way', 
    r'MeaWallet', r'Meituan Pay', r'Mercado Pago', r'MobiKwik', 
    r'MobilePay', r'Moka', r'MoneyGram', r'MoneyNetint', 
    r'Monri', r'Mpay', r'Multibanco', r'N26', 
    r'Neteller', r'Newegg', r'NextPay', r'NganLuong', 
    r'Nium', r'NomuPay', r'North Payments', r'One97', 
    r'OpenNode', r'OXXO', r'PagBrasil', r'PagSeguro', 
    r'PayBright', r'PayJunction', r'PayMaya', r'Payone', 
    r'PayPal Credit', r'PayPlug', r'Paysafecard', r'PaySimple', 
    r'PayTabs',r'GammaWallet', r'DeltaCheckout', r'EpsilonPay', r'ThetaCash', 
    r'ZetaFunds', r'OmegaTransfer', r'SigmaPayments', r'LambdaPay', 
    r'NuWallet', r'XiPayment', r'OmicronCash', r'PiFunds', 
    r'RhoTransfer', r'TauCheckout', r'UpsilonPay', r'PhiWallet', 
    r'ChiPayments', r'PsiFunds', r'EpsilonExpress', r'ThetaTransfer', 
    r'ZetaCash', r'OmegaExpress', r'SigmaTransfer', r'LambdaFunds', 
    r'NuPay', r'XiWallet', r'OmicronPayments', r'PiTransfer', 
    r'RhoCheckout', r'TauCash', r'UpsilonFunds', r'PhiExpress', 
    r'ChiTransfer', r'PsiCash', r'AlphaExpress', r'BetaPay', 
    r'GammaFunds', r'DeltaTransfer', r'EpsilonWallet', r'ThetaPayments', 
    r'ZetaTransfer', r'OmegaFunds', r'SigmaWallet', r'LambdaExpress', 
    r'NuFunds', r'XiCash', r'OmicronPay', r'PiWallet', 
    r'RhoPayments', r'TauTransfer', r'UpsilonCash', r'PhiFunds', 
    r'ChiExpress', r'PsiTransfer', r'AlphaCash', r'BetaFunds', 
    r'GammaTransfer', r'DeltaWallet', r'EpsilonPayments', r'ThetaExpress', 
    r'ZetaTransfer', r'OmegaFunds', r'SigmaPay', r'LambdaWallet', 
    r'NuTransfer', r'XiExpress', r'OmicronFunds', r'PiCash',  r'Paytend', r'PayTrace', r'PayU Latam', 
    r'Payvision',r'Payouts', r'AWS', r'Peach Payments', r'Pes', r'CPA', 
    r'Payouts', r'AWS', 
    # Add more fictional or lesser-known gateways to reach 700
    r'GammaWallet', r'DeltaCheckout', r'EpsilonPay',r'ZellePay', r'Tikkie', r'Lyra', r'Vantiv', r'BillMatrix', r'TSYS',
    r'Netgiro', r'Payone', r'Paysera', r'Sisow', r'MyBank', r'ApplePay', 
    r'GoPay', r'TigoMoney', r'PayMaya', r'Shopify Payments', r'Rave', 
    r'Wepay', r'ProPay', r'Khipu', r'NextPay', r'QNB eFinans', 
    r'Viva Payments', r'Fawry', r'Masterpass', r'PugglePay', r'MyGate', 
    r'Payza', r'Paytrail', r'Paybox', r'Qiwi', r'Rambus', r'Yandex.Money',
    r'MobilePay', r'PingPong', r'Payoneer', r'Plastiq', r'Venmo', 
    r'Cashfree', r'KakaoPay', r'Mint', r'Fintiv', r'PayZapp', r'MoMo', 
    r'PayMe', r'Payhere', r'PayGo', r'Paysera', r'Payscout', r'PointCheckout', 
    r'2C2P', r'PayGate', r'PayDash', r'Payzaar', r'PayWay', r'PayRequest', 
    r'PayPlug', r'Paysafe', r'Paysbuy', r'Paydirekt', r'Peach Payments', 
    r'Pecunpay', r'PayFazz', r'PayXpert', r'PayFair', r'Paylution', 
    r'Paylike', r'Payza', r'Paybox', r'PayByLink', r'PayByFace', 
    r'Payeezy', r'PayEx', r'Payfirma', r'Paytrace', r'Payworks', 
    r'Paytm', r'PayU', r'Payvision', r'Payza', r'Payzippy', r'Pingit', 
    r'PlanetPayment', r'Przelewy24', r'Pyypl', r'Paysend', r'Paya', 
    r'Qonto', r'QuickBooks Payments', r'QuickPay', r'Rabobank', r'Razorpay', 
    r'Recurly', r'Revolut Business', r'Saferpay', r'Satispay', r'SecurePay', 
    r'Sezzle', r'Shopify Payments', r'Skrill', r'SmartPay', r'Square', 
    r'Stripe', r'SumoPay', r'SunCash', r'Tab', r'Tapp', r'Tappay', 
    r'Telr', r'Tikkie', r'TimiPay', r'TransferGo', r'Trustly', r'Twint', 
    r'Uala', r'Uangku', r'Upay', r'Vantiv', r'Venmo', r'Vigo', r'VivaWallet', 
    r'VodaPay', r'VoguePay', r'Vopay', r'Vpos', r'WeChat Pay', r'WebMoney', 
    r'WireBarley', r'Worldline', r'WorldRemit', r'WoraPay', r'Xendpay', 
    r'Xoom', r'Yandex.Money', r'Yapstone', r'Yoco', r'ZainCash', 
    r'Zapp', r'Zelle', r'ZellePay', r'ZigPay', r'Zimpler', r'ZipMoney', 
    r'ZipPay', r'ZipZap', r'ZomatoPay', r'Zotapay', r'Zuora', 
    r'ZellePay', r'Tikkie', r'Lyra', r'Vantiv', r'BillMatrix', r'TSYS', 
    r'Netgiro', r'Payone', r'Paysera', r'Sisow', r'MyBank', r'ApplePay', 
    r'GoPay', r'TigoMoney', r'PayMaya', r'Shopify Payments', r'Rave', 
    r'Wepay', r'ProPay', r'Khipu', r'NextPay', r'QNB eFinans', 
    r'Viva Payments', r'Fawry', r'Masterpass', r'PugglePay', r'MyGate', 
    r'Payza', r'Paytrail', r'Paybox', r'Qiwi', r'Rambus', r'Yandex.Money',
    r'MobilePay', r'PingPong', r'Payoneer', r'Plastiq', r'Venmo', 
    r'Cashfree', r'KakaoPay', r'Mint', r'Fintiv', r'PayZapp', r'MoMo', 
    r'PayMe', r'Payhere', r'PayGo', r'Paysera', r'Payscout', r'PointCheckout', 
    r'2C2P', r'PayGate', r'PayDash', r'Payzaar', r'PayWay', r'PayRequest', 
    r'PayPlug', r'Paysafe', r'Paysbuy', r'Paydirekt', r'Peach Payments', 
    r'Pecunpay', r'PayFazz', r'PayXpert', r'PayFair', r'Paylution', 
    r'Paylike', r'Payza', r'Paybox', r'PayByLink', r'PayByFace', 
    r'Payeezy', r'PayEx', r'Payfirma', r'Paytrace', r'Payworks', 
    r'Paytm', r'PayU', r'Payvision', r'Payza', r'Payzippy', r'Pingit', 
    r'PlanetPayment', r'Przelewy24', r'Pyypl', r'Paysend', r'Paya', 
    r'Qonto', r'QuickBooks Payments', r'QuickPay', r'Rabobank', r'Razorpay', 
    r'Recurly', r'Revolut Business', r'Saferpay', r'Satispay', r'SecurePay', 
    r'Sezzle', r'Shopify Payments', r'Skrill', r'SmartPay', r'Square', 
    r'Stripe', r'SumoPay', r'SunCash', r'Tab', r'Tapp', r'Tappay', 
    r'Telr', r'Tikkie', r'TimiPay', r'TransferGo', r'Trustly', r'Twint', 
    r'Uala', r'Uangku', r'Upay', r'Vantiv', r'Venmo', r'Vigo', r'VivaWallet', 
    r'VodaPay', r'VoguePay', r'Vopay', r'Vpos', r'WeChat Pay', r'WebMoney', 
    r'WireBarley', r'Worldline', r'WorldRemit', r'WoraPay', r'Xendpay', 
    r'Xoom', r'Yandex.Money', r'Yapstone', r'Yoco', r'ZainCash', 
    r'Zapp', r'Zelle', r'ZellePay', r'ZigPay', r'Zimpler', r'ZipMoney', 
    r'ZipPay', r'ZipZap', r'ZomatoPay', r'Zotapay', r'Zuora', r'ThetaCash', 
    
]


    for gateway in gateways:
        if re.search(gateway, content, re.IGNORECASE) or soup.find(string=re.compile(gateway, re.IGNORECASE)):
            payment_methods.append(gateway)

    return list(set(payment_methods))

async def check_security_features_async(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = await fetch_url(url)
    if response is None:
        return False, False

    has_recaptcha = 'recaptcha' in response.lower() or 'g-recaptcha' in response.lower()
    has_cloudflare = 'cf-browser-verification' in response.lower() or 'cloudflare' in response.lower()

    return has_recaptcha, has_cloudflare

async def handle_url_check(url):
    payment_methods_task = check_payment_gateway_async(url)
    security_features_task = check_security_features_async(url)

    payment_methods, (has_recaptcha, has_cloudflare) = await asyncio.gather(payment_methods_task, security_features_task)

    return payment_methods, has_recaptcha, has_cloudflare

def create_custom_buttons(viled_count, dead_count, number_of_gateways, current_url):
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(f"• Url ➜ {current_url} •", callback_data='url'),
        types.InlineKeyboardButton(f"• Viled ✅ ➜ [ {viled_count} ] •", callback_data='viled'),
        types.InlineKeyboardButton(f"• Dead ❌ ➜ [ {dead_count} ] •", callback_data='dead'),
        types.InlineKeyboardButton(f"• Number ➜ [ {number_of_gateways} ] •", callback_data='number'),
        types.InlineKeyboardButton("[ 𝐒𝐓𝐎𝐏 ]", callback_data='stop')
    ]
    for button in buttons:
        markup.add(button)
    return markup

def create_dev_button():
    markup = types.InlineKeyboardMarkup()
    dev_button = types.InlineKeyboardButton("𝐃𝐄𝐕", url="https://t.me/ccdropshq")
    markup.add(dev_button)
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "scan_from_file")
def allow_scanning_handler(call):
    global allow_scanning
    allow_scanning = True
    bot.send_message(call.message.chat.id, "Please send the portals file now.")

@bot.callback_query_handler(func=lambda call: call.data == "stop")
def stop_scanning_handler(call):
    global stop_scanning
    stop_scanning = True
    bot.send_message(call.message.chat.id, "The scan has been stopped..")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    global stop_scanning, allow_scanning
    if not allow_scanning:
        bot.send_message(message.chat.id, "Please click the 'Check Combo Gates' button first.")
        return

    if message.document.mime_type == "text/plain":
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        urls = downloaded_file.decode('utf-8').splitlines()

        viled_count = 0
        dead_count = 0
        number_of_gateways = len(urls)

        stop_scanning = False
        buttons_message = bot.send_message(message.chat.id, "Start the scan....", reply_markup=create_custom_buttons(viled_count, dead_count, number_of_gateways, ""))
        for url in urls:
            if url.startswith("http") and not stop_scanning:
                asyncio.run(process_and_send_result(url, message.chat.id, buttons_message, viled_count, dead_count, number_of_gateways))

async def process_and_send_result(url, chat_id, buttons_message, viled_count, dead_count, number_of_gateways):
    global stop_scanning
    if stop_scanning:
        return

    payment_methods, has_recaptcha, has_cloudflare = await handle_url_check(url)

    if payment_methods:
        viled_count += 1
    else:
        dead_count += 1

    response_message = (
        "╭────── • ◈ • ──────╮\n\n"
        "     Good Extraction 🟢\n\n"
        f"𝗦𝗜𝗧𝗘 ⮕ {url}\n\n"
        f"𝗣𝗔𝗬𝗠𝗘𝗡𝗧 ⮕ {payment_methods if payment_methods else 'There are no known payment gateways.'}\n\n"
        f"𝗖𝗔𝗣𝗧𝗖𝗛𝗔 ⮕ {'True ⚠️' if has_recaptcha else 'False ❌'}\n\n"
        f"𝗖𝗟𝗢𝗨𝗗𝗙𝗟𝗔𝗥𝗘 ⮕ {'True ✅' if has_cloudflare else 'False ❌'}\n\n"
        "𝗕?? ⮕ @LOST_VENOM\n"
        "╰────── • ◈ • ──────╯"
    )

    # Send the result message with the image and DEV button
    bot.send_photo(chat_id=chat_id, photo="https://t.me/CF_1C/7", caption=response_message, reply_markup=create_dev_button())

    # Update the existing buttons message with new counts and current URL
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=buttons_message.message_id, reply_markup=create_custom_buttons(viled_count, dead_count, number_of_gateways, url))

def create_button():
    markup = types.InlineKeyboardMarkup()
    scan_button = types.InlineKeyboardButton("Checking the gates of Comp", callback_data="scan_from_file")
    dev_button = types.InlineKeyboardButton("𝐃𝐄𝐕", url="https://t.me/ccdropshq")
    markup.add(scan_button)
    markup.add(dev_button)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    id = message.from_user.id
    with open('data.json', 'r') as json_file:
        json_data = json.load(json_file)

    if str(id) not in json_data:
        bot.send_photo(chat_id=message.chat.id,
                       photo="https://t.me/CF_1C/7",
                       caption="╭────── • ◈ • ──────╮\n\n◉ Please subscribe to the bot via the subscription code that you get from the bot admin. Please buy it to use the bot 🪽\n\nPlease subscribe to the bot by emailing the admin and he will give you the activation code. 🟢\n╰────── • ◈ • ──────╯",
                       reply_markup=create_button())
    else:
        bot.send_photo(chat_id=message.chat.id,
                       photo="https://t.me/CF_1C/7",
                       caption="╭────── • ◈ • ──────╮\n\n◉ Gate Scanning Bot 🟢\n\nـــــــــــــــــــــــــــــــــــــ\n\nPlease send the portal link as follows : \n\n/g + url\n\n╰────── • ◈ • ──────╯",
                       reply_markup=create_button())

@bot.message_handler(commands=["code"])
def start(message):
    def my_function():
        user_id = message.from_user.id
        if not user_id == admin:
            bot.reply_to(message, "You do not have permission to use this command.")
            return
        try:
            h = float(message.text.split(' ')[1])
            characters = string.ascii_uppercase + string.digits
            pas = f'{namebot}-' + ''.join(random.choices(characters, k=4)) + '-' + ''.join(random.choices(characters, k=4)) + '-' + ''.join(random.choices(characters, k=4))
            current_time = datetime.now()
            ig = current_time + timedelta(hours=h)
            plan = 'premium'
            if 'VIP' in message.text:
                plan = 'VIP'
            parts = str(ig).split(':')
            ig = ':'.join(parts[:2])

            with open('data.json', 'r+') as json_file:
                json_data = json.load(json_file)
                new_data = {
                    pas: {
                        "plan": plan,
                        "time": ig,
                    }
                }
                json_data.update(new_data)
                json_file.seek(0)
                json.dump(json_data, json_file, indent=4)
                json_file.truncate()

            msg = f'''<b>╭────── • ◈ • ──────╮

◉ NEW CODE 🟢

ــــــــــــــــــــــــــــــــــــــ
الكــود ~ <code>{pas}</code>

subscribe

Subscription ~ VIP

Code ~ /redeem

╰────── • ◈ • ──────╯</b>'''

            bot.reply_to(message, msg, parse_mode="HTML")
        except Exception as e:
            print('ERROR : ', e)
            bot.reply_to(message, str(e), parse_mode="HTML")

    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(func=lambda message: message.text.lower().startswith('.redeem') or message.text.lower().startswith('/redeem'))
def respond_to_redeem(message):
    def my_function():
        try:
            user_id = message.from_user.id
            code = message.text.split(' ')[1]

            with open('data.json', 'r+') as file:
                json_data = json.load(file)
                if code not in json_data:
                    bot.reply_to(message, '''<b>╭────── • ◈ • ──────╮

◉ Wrong code ❌

ــــــــــــــــــــــــــــــ

The activation is incorrect or has been used before❌
    
╰────── • ◈ • ──────╯</b>''', parse_mode="HTML")
                    return

                timer = json_data[code]['time']
                plan = json_data[code]["plan"]

                json_data[str(user_id)] = {
                    "plan": plan,
                    "timer": timer,
                    "funds": 0,
                    "order": ""
                }

                del json_data[code]
                file.seek(0)
                json.dump(json_data, file, indent=4)
                file.truncate()

            keyboard = types.InlineKeyboardMarkup()
            free = types.InlineKeyboardButton(text='𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬', callback_data='menu')
            keyboard.row(free)

            msg = f'''<b>╭────── • ◈ • ──────╮

◉ You have successfully subscribed 🟢

ــــــــــــــــــــــــــــــــــــ

تــSuccessfully subscribed to the bot 💸:

Subscribe ~ {timer}   

Ak ~ VIP 🟢

╰────── • ◈ • ──────╯</b>'''
            bot.reply_to(message, msg, reply_markup=keyboard)

        except Exception as e:
            print('ERROR : ', e)
            bot.reply_to(message, '''<b>╭────── • ◈ • ──────╮

◉ Wrong code ❌

ــــــــــــــــــــــــــــــ

The activation code is incorrect or has been used before❌
    
╰────── • ◈ • ──────╯</b>''', parse_mode="HTML")

    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(commands=['g'])
def handle_message(message):
    async def process_url_check():
        user_id = message.from_user.id
        with open('data.json', 'r') as json_file:
            json_data = json.load(json_file)

        if str(user_id) not in json_data:
            bot.send_photo(
                chat_id=message.chat.id,
                photo="https://t.me/CF_1C/7",
                caption="╭────── • ◈ • ──────╮\n\n◉ Please subscribe to the bot via the subscription code that you get from the bot admin. Please buy it to use the bot 🪽\n\nPlease subscribe to the bot by emailing the admin and he will give you the activation code. 🟢\n╰────── • ◈ • ──────╯",
                reply_markup=create_dev_button()
            )
            return

        url_parts = message.text.strip().split(' ', 1)
        if len(url_parts) < 2:
            bot.send_photo(
                chat_id=message.chat.id,
                photo="https://t.me/CF_1C/7",
                caption="╭────── • ◈ • ──────╮\n\n◉ Worng ❌\n\nـــــــــــــــــــــــــــــ\n\nPlease send the link correctly as follows:\n/g **** \n\n╰────── • ◈ • ──────╯",
                reply_markup=create_dev_button()
            )
            return

        url = url_parts[1].strip()
        parsed_url = urlparse(url)

        if not parsed_url.scheme:
            bot.send_photo(
                chat_id=message.chat.id,
                photo="https://t.me/CF_1C/7",
                caption="╭────── • ◈ • ──────╮\n\n◉ Worng ❌\n\nـــــــــــــــــــــــــــــ\n\nAn error occurred, please make sure that the gateway is sent correctly❗\n\n╰────── • ◈ • ──────╯",
                reply_markup=create_dev_button()
            )
            return

        checking_message = bot.send_photo(
            chat_id=message.chat.id,
            photo="https://t.me/CF_1C/7",
            caption=f"╭────── • ◈ • ──────╮\n\n◉ 𝗖𝗛𝗘𝗖𝗞𝗜𝗡𝗚 𝗬𝗢𝗨𝗥 𝗨𝗥𝗟...⌛\n\n╰────── • ◈ • ──────╯",
            reply_markup=create_dev_button()
        )

        payment_methods, has_recaptcha, has_cloudflare = await handle_url_check(url)

        response_message = (
            "╭────── • ◈ • ──────╮\n\n"
            "     Good Extraction 🟢\n\n"
            "ــــــــــــ\n"
            f"𝗦𝗜𝗧𝗘 ⮕ {url}\n\n"
            f"𝗣𝗔𝗬𝗠𝗘𝗡𝗧 ⮕ {payment_methods if payment_methods else 'There are no known payment gateways.'}\n\n"
            f"𝗖𝗔𝗣𝗧𝗖𝗛𝗔 ⮕ {'True ⚠️' if has_recaptcha else 'False ❌'}\n\n"
            f"𝗖𝗟𝗢𝗨𝗗𝗙𝗟𝗔𝗥𝗘 ⮕ {'True ✅' if has_cloudflare else 'False ❌'}\n\n"
            "𝗕𝗬 ⮕ @AM_E_R_R_O_R\n"
            "╰────── • ◈ • ──────╯"
        )

        bot.delete_message(chat_id=checking_message.chat.id, message_id=checking_message.message_id)
        bot.send_photo(chat_id=message.chat.id, photo="https://t.me/CF_1C/7", caption=response_message, reply_markup=create_dev_button())

    asyncio.run(process_url_check())

print('The bot has been launched')
bot.infinity_polling()
