import qrcode

# Replace this with your Opay or Palmpay payment link
payment_url = "https://pay.opay.com/your-business-link"  # Example: Opay merchant link

# Generate QR code
img = qrcode.make(payment_url)
img.save("static/images/opay_qr.png")
print("QR code saved as static/images/opay_qr.png")
