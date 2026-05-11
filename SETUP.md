# 📚 WhatsApp Book Bot — Setup Guide

## Step 1: Install Python
Download from https://python.org (version 3.10 or newer)

## Step 2: Install dependencies
Open terminal/command prompt in this folder and run:
```
pip install -r requirements.txt
```

## Step 3: Get Meta Credentials
1. Go to https://developers.facebook.com
2. Create a new App → choose "Business"
3. Add "WhatsApp" product
4. Go to WhatsApp → API Setup
5. Copy your:
   - Phone Number ID
   - Temporary Access Token

## Step 4: Add your credentials to app.py
Open app.py and fill in:
```python
PHONE_NUMBER_ID = "paste your Phone Number ID here"
ACCESS_TOKEN    = "paste your Access Token here"
```

## Step 5: Add your real phone number in Meta Dashboard
- In WhatsApp → API Setup → Add Phone Number
- Enter: +254798734442
- Verify via OTP sent to your phone

## Step 6: Run the bot locally (for testing)
```
python app.py
```

## Step 7: Expose to internet for testing (use ngrok)
Download ngrok from https://ngrok.com, then run:
```
ngrok http 5000
```
Copy the https URL it gives you (e.g. https://abc123.ngrok.io)

## Step 8: Set Webhook in Meta Dashboard
- Go to WhatsApp → Configuration → Webhook
- URL: https://abc123.ngrok.io/webhook
- Verify Token: mybookbot
- Click Verify

## Step 9: Deploy to Render.com (free hosting)
1. Push code to GitHub
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set Start Command: gunicorn app:app
5. Deploy — Render gives you a permanent URL

## Step 10: Update Webhook URL
Replace ngrok URL with your Render URL in Meta Dashboard

## Customizing Your Bot
- Edit the BOOKS dictionary in app.py to add your real books
- Update delivery prices and M-Pesa paybill number
- Add more menu options as needed

## Support
For help with Meta API: https://developers.facebook.com/docs/whatsapp
For M-Pesa Daraja API: https://developer.safaricom.co.ke
