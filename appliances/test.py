import time
import random

# Define character and mood
lines = [
    ("👨‍💻 Programmer", "System चल्दैन, Client भन्छ – 'तपाईंको bug हो' 🐞"),
    ("🧠 Brain", "Syntax error हो कि Logic error? सोच्दा सोच्दै सिर दुख्यो 😵‍💫"),
    ("💻 Laptop", "म त थाकें! VSCode नै २GB RAM खाइराछ 😩"),
    ("☕ Coffee", "एक कप मलाई पनि दिनु, मैले पनि debug गर्नुछ 🤖"),
    ("👻 Bug", "म त कहाँ हराएँ? तपाईंले नै मलाई जन्माउनु भएको हो 😈"),
    ("🧘 Programmer", "ध्यान गरौं... except block ले सब थाम्छ 😌"),
    ("👨‍💻 Programmer", "Finally: `print('Done')` तर client ले भन्छ – यो feature त भएन 😐"),
    ("😵 System", "Compilation सफल भयो... तर चलाउँदा `segmentation fault` आयो 🤯"),
    ("🎉 ChatGPT", "Don't worry, yo sab fix गरिदिन्छु 😎"),
    ("🚀 Life", "Production मा push गर्‍यो, अनि छुट्टी मनाउन जान मिल्छ अब 🎉")
]

# Funny effects for random reactions
emojis = ["🤣", "🤔", "🫠", "🙃", "👾", "😱", "🪲", "🚨", "📉", "🧨"]

# Print with delay
for role, dialog in lines:
    react = random.choice(emojis)
    print(f"{role}: {dialog} {react}")
    time.sleep(1.2)