# Firebase Setup for Dealer Portal

1. Go to https://console.firebase.google.com
2. Click "Add Project" → Give it a name → Click Next
3. Disable Google Analytics → Click Create Project
4. After it's created, go to the left menu:
   - Click "Authentication"
   - Click "Get Started"
   - Under Sign-in methods → Enable "Email/Password"
5. Now go to "Project Settings" (⚙️ gear icon at top left)
6. Click "Service Accounts" tab
7. Click "Generate new private key"
8. It will download a `.json` file
9. Move that `.json` file into your project folder (`battery_dealer_portal`)
10. In `.env.example`, set:
    FIREBASE_CRED_PATH=your_filename.json