document.getElementById("strp").addEventListener("click", () => {

  //stripe  
  // Get Stripe publishable key
      fetch('/config')
      .then((result) => { return result.json(); })
      .then((data) => {
        // Initialize Stripe.js
        const stripe = Stripe(data.publicKey);
  
    // Event handler
      // Get Checkout Session ID
        fetch('/create-checkout-session')
        .then((result) => { return result.json(); })
        .then((data) => {
          console.log(data);
        // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
          console.log(res);
        });
    });
  
  
  });
  
  
  document.getElementById("rzrp").addEventListener("click", () => {
  
  //razorpay
  fetch('/razorpay')
  .then((result) => { return result.json(); })
  .then((data) => {
    // Initialize js
    console.log(data)
    const rzp1 = new Razorpay(data.options);
      rzp1.open()
      .then((res) => {
          console.log(res);
          // Redirect 
    });
  });
  
  
  })
  
  //paypal
  
  var CREATE_PAYMENT_URL  = 'http://127.0.0.1:5000/payment';
  var EXECUTE_PAYMENT_URL = 'http://127.0.0.1:5000/execute';
  
      paypal.Button.render({
  
          env: 'sandbox', // Or 'sandbox'
  
          commit: true, // Show a 'Pay Now' button
  
          payment: function() {
              return paypal.request.post(CREATE_PAYMENT_URL).then(function(data) {
                  console.log(data)
                  return data.paymentID;
              });
          },
  
          onAuthorize: function(data) {
              return paypal.request.post(EXECUTE_PAYMENT_URL, {
                  paymentID: data.paymentID,
                  payerID:   data.payerID
              }).then(function(res) {
  
                  console.log(res.success)
                  // The payment is complete!
                  // You can now show a confirmation message to the customer
              });
          }
  
      }, '#paypal-button');
  