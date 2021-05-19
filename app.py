import os
import stripe
from flask import Flask, jsonify, render_template, request
import razorpay
import paypalrestsdk
import json


app = Flask(__name__)


#app = Flask(__name__,static_folder = "static", static_url_path='')
razorpay_client = razorpay.Client(auth=("rzp_test_8ydfJQKGSKoloz", "7LNONq8PYWjg4ImLujHDxpst"))
order_id = ''
params_dict = {}

'''
razorpay_keys = {
    "key_id" : os.environ["RZRP_KEY_ID"],
    "key" : os.environ["RZRP_KEY"]
}
'''

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AW44lrpC2Jjw6OE3_0p-xWl2xA8FmjsFL9JmlQW4pSb3y4_1oIa0sRORUGXk9tGHtghP_WoWMHsHQ225",
  "client_secret": "EK8iQR2uy557Cxed44wfEWaK5IQ5ZjiVLL1yg_G6zHC7y_Vk4GOmGO6LNOB7B4K7qmtEcMhWHJqfZ46b" })

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"],
}

stripe.api_key = stripe_keys["secret_key"]



def app_create():
    order_amount = 50000
    order_currency = 'INR'
    order_receipt = 'order_rcptid_100'
    notes = {'Shipping address': 'Pune, Maharashtra'}
    something = razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
    return something['id']



def success():
    return render_template("success.html")


def cancelled():
    return render_template("cancelled.html")


'''
@app.route('/charge', methods=['POST'])
def rzrp_charge():
    amount = 5100
    payment_id = request.form['razorpay_payment_id']
    razorpay_client.payment.capture(payment_id, amount)
    return json.dumps(razorpay_client.payment.fetch(payment_id))
'''

@app.route("/")
def index():
    return render_template("index.html")

#stripe 

@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)


@app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://localhost:5000/"
    stripe.api_key = stripe_keys["secret_key"]

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": "T-shirt",
                    "quantity": 1,
                    "currency": "inr",
                    "amount": "2000",
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403



def handle_checkout_session(session):
    print("Payment was successful.")
    # TODO: run some custom code here


@app.route("/success")
def success_redirect():
    success()


@app.route("/cancelled")
def cancelled_redirect():
    cancelled()


#razorpay

@app.route('/razorpay')
def app_pay():

    order_id = app_create()
    params_dict['razorpay_order_id'] = order_id


    razrp_config = {
        "options" : {
                        "key": "rzp_test_8ydfJQKGSKoloz",
                        "amount": "50000",
                        "currency": "INR",
                        "name": "BCT",
                        "description": "Test Transaction",
                        "order_id": order_id,
                        "callback_url": "http://127.0.0.1:5000/checkout",
                        "notes": {
                                    "address": "Razorpay Corporate Office"
                                },
                        "theme": {
                                "color": "#3399cc"
                            } 
                }
    }
    return jsonify(razrp_config)


@app.route('/checkout', methods=['POST'])
def app_charge():
    amount = 50000
    payment_id = request.form['razorpay_payment_id']
    signature = request.form['razorpay_signature']
    
    params_dict['razorpay_payment_id'] = payment_id
    params_dict['razorpay_signature'] = signature

    result = razorpay_client.utility.verify_payment_signature(params_dict)

    if result == None:
        success()
    else:
        cancelled()


#paypal

@app.route('/payment', methods=['POST'])
def payment():

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": "500.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "500.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

@app.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})


if __name__ == "__main__":
    app.run()
