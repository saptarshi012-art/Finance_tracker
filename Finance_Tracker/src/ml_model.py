from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# CATEGORY EXAMPLES
# ============================================================
CATEGORY_EXAMPLES = {

    "Food": [
        # Meals & dining
        "pizza", "burger", "sandwich", "pasta", "noodles", "biryani", "rice",
        "dal", "roti", "paratha", "idli", "dosa", "poha", "upma", "maggi",
        "soup", "salad", "sushi", "wrap", "taco", "shawarma", "kebab",
        "momos", "dimsum", "fried rice", "chowmein", "thali", "curry",
        # Restaurants & delivery
        "restaurant", "dhaba", "food court", "canteen", "hotel dining",
        "dinner", "lunch", "breakfast", "brunch", "supper", "snacks",
        "swiggy", "zomato", "food order", "food delivery", "takeaway",
        "dominos", "mcdonalds", "kfc", "subway", "pizza hut", "burger king",
        "cafe", "coffee shop", "bakery", "juice bar", "tea stall",
        "starbucks", "barista", "chai", "coffee", "tea", "juice", "smoothie",
        # Groceries & cooking
        "groceries", "grocery store", "supermarket", "vegetables", "fruits",
        "milk", "eggs", "bread", "butter", "cheese", "paneer", "meat",
        "chicken", "fish", "mutton", "dal", "rice bag", "flour", "oil",
        "spices", "condiments", "snacks", "biscuits", "chips", "sweets",
        "mithai", "ice cream", "chocolate", "candy", "dry fruits", "nuts",
        # Drinks & others
        "cold drink", "soft drink", "beer", "wine", "alcohol", "whiskey",
        "water bottle", "energy drink", "protein shake",
    ],

    "Transport": [
        # Ride-hailing & taxis
        "uber", "ola", "rapido", "cab", "taxi", "auto rickshaw", "auto ride",
        "bike taxi", "meru cab", "radio cab", "city cab",
        # Public transport
        "bus ticket", "bus pass", "metro card", "metro travel", "metro token",
        "local train", "train journey", "railway ticket", "irctc booking",
        "monorail", "tram", "ferry ride", "boat ride", "water taxi",
        # Long distance
        "flight ticket", "airfare", "plane ticket", "air india", "indigo",
        "spicejet", "vistara", "goair", "airline booking",
        "bus booking", "volvo bus", "sleeper bus", "redbus",
        "train booking", "tatkal ticket", "ac coach",
        # Personal vehicle
        "petrol", "diesel", "fuel", "cng", "car fuel", "bike fuel",
        "vehicle service", "car service", "bike service", "oil change",
        "tyre puncture", "car repair", "bike repair", "mechanic",
        "car wash", "vehicle insurance", "road tax", "fastag", "toll",
        "parking fee", "parking charge",
        # Rentals & misc
        "car rental", "bike rental", "scooter rental", "vehicle hire",
        "driver salary", "driver payment", "monthly transport pass",
    ],

    "Shopping": [
        # Clothing & fashion
        "clothes", "clothing", "shirt", "t-shirt", "jeans", "trousers",
        "dress", "saree", "kurta", "suit", "jacket", "hoodie", "sweater",
        "shoes", "sneakers", "sandals", "heels", "boots", "slippers",
        "bag", "handbag", "backpack", "purse", "wallet", "belt",
        "watch", "sunglasses", "jewellery", "earrings", "necklace", "ring",
        "accessories", "socks", "underwear", "innerwear", "sportswear",
        # Electronics & gadgets
        "mobile phone", "smartphone", "laptop", "computer", "tablet", "ipad",
        "headphones", "earphones", "earbuds", "airpods", "speaker",
        "charger", "power bank", "cable", "adapter", "keyboard", "mouse",
        "monitor", "tv", "led tv", "smart tv", "camera", "printer",
        "pen drive", "hard disk", "ssd", "memory card", "router", "wifi",
        "smartwatch", "fitness band", "gaming console", "playstation", "xbox",
        # Online shopping
        "amazon", "flipkart", "myntra", "meesho", "ajio", "nykaa",
        "snapdeal", "bigbasket", "blinkit", "zepto", "online order",
        "online shopping", "e-commerce", "shopping app",
        # Home & furniture
        "furniture", "sofa", "bed", "mattress", "table", "chair", "wardrobe",
        "curtains", "bedsheet", "pillow", "blanket", "lamp", "fan", "cooler",
        "washing machine", "refrigerator", "microwave", "mixer grinder",
        "utensils", "cookware", "crockery", "home decor", "plants",
        # Books & stationery
        "books", "novel", "textbook", "notebook", "pen", "pencil",
        "stationery", "diary", "planner", "art supplies", "craft",
        # Gifts & misc
        "gift", "gift card", "voucher", "present", "flowers", "bouquet",
        "toy", "kids toy", "board game", "puzzle",
    ],

    "Entertainment": [
        # Streaming & subscriptions
        "netflix", "amazon prime", "hotstar", "disney plus", "zee5",
        "sonyliv", "jiocinema", "voot", "mxplayer", "apple tv",
        "spotify", "gaana", "wynk", "jiosaavn", "youtube premium",
        "subscription", "ott subscription", "streaming service",
        # Movies & shows
        "movie ticket", "cinema", "pvr", "inox", "multiplex",
        "movie outing", "film festival", "drive-in movie",
        # Gaming
        "gaming", "video game", "pc game", "mobile game", "playstation",
        "xbox game", "steam", "epic games", "in-app purchase", "game credits",
        "gaming cafe", "esports", "gaming tournament",
        # Live events
        "concert", "live show", "music festival", "comedy show", "stand-up",
        "theatre", "play", "opera", "ballet", "cultural event",
        "sports match", "ipl ticket", "cricket match", "football match",
        "stadium entry", "event ticket", "bookmyshow",
        # Recreation & hobbies
        "amusement park", "theme park", "water park", "zoo", "aquarium",
        "museum", "art gallery", "exhibition", "science centre",
        "bowling", "laser tag", "escape room", "go-karting",
        "billiards", "pool table", "arcade", "virtual reality",
        # Travel & leisure
        "trip", "vacation", "holiday", "tour", "sightseeing",
        "hotel stay", "resort", "airbnb", "hostel", "weekend getaway",
        "travel package", "trekking", "camping", "adventure sport",
        "bungee jumping", "skydiving", "river rafting", "scuba diving",
        # Sports & fitness hobbies
        "gym membership", "yoga class", "dance class", "swimming",
        "sports equipment", "cricket bat", "football", "badminton",
        "tennis", "cycling", "hiking", "photography", "painting class",
        # Social & nightlife
        "party", "club", "lounge", "bar", "pub", "nightout",
        "karaoke", "dj night", "birthday party", "celebration",
    ],

    "Rent": [
        # Housing rent
        "house rent", "flat rent", "apartment rent", "room rent",
        "monthly rent", "rent payment", "pg rent", "hostel rent",
        "studio rent", "bhk rent", "1bhk", "2bhk", "3bhk",
        # Commercial rent
        "office rent", "shop rent", "warehouse rent", "commercial rent",
        "co-working space", "desk rental", "office space",
        # Lease & agreements
        "lease payment", "lease installment", "rental agreement",
        "security deposit", "advance rent", "token advance",
        # Property related
        "property tax", "society maintenance", "maintenance charges",
        "society fee", "building charges", "flat maintenance",
        "water charges", "parking charges", "lift charges",
        # Temporary stays
        "guest house", "service apartment", "paying guest",
        "short term rental", "temporary accommodation",
    ],

    "Others": [
        # Healthcare & medical
        "doctor visit", "hospital", "clinic", "pharmacy", "medicine",
        "prescription", "health checkup", "blood test", "lab test",
        "xray", "scan", "mri", "dental", "dentist", "optician",
        "spectacles", "contact lens", "surgery", "ambulance",
        "health insurance", "medical insurance", "ayurvedic", "homeopathic",
        # Education & learning
        "school fees", "college fees", "tuition fees", "coaching",
        "online course", "udemy", "coursera", "skill course",
        "workshop", "seminar", "certification", "exam fee",
        "books fee", "library fee", "hostel fee", "bus fee",
        # Utilities & bills
        "electricity bill", "water bill", "gas bill", "internet bill",
        "broadband", "wifi bill", "mobile recharge", "phone bill",
        "dth recharge", "cable tv", "newspaper", "magazine",
        "lpg cylinder", "cooking gas", "piped gas",
        # Banking & finance
        "emi", "loan payment", "credit card bill", "bank charge",
        "atm charge", "transaction fee", "insurance premium",
        "life insurance", "vehicle insurance", "fd investment",
        "mutual fund", "sip", "stock purchase", "tax payment",
        # Personal care & grooming
        "salon", "haircut", "spa", "massage", "facial", "pedicure",
        "manicure", "threading", "waxing", "beauty parlour",
        "skincare", "perfume", "cosmetics", "makeup", "deodorant",
        "shampoo", "soap", "toiletries", "personal hygiene",
        # Home services & maintenance
        "plumber", "electrician", "carpenter", "painter", "repair",
        "home repair", "appliance repair", "ac service", "pest control",
        "house cleaning", "maid salary", "domestic help", "cook salary",
        "laundry", "dry cleaning", "ironing",
        # Charity & social
        "donation", "charity", "temple donation", "religious offering",
        "festival expenses", "pooja expenses", "wedding gift",
        "funeral expenses", "social gathering",
        # Miscellaneous
        "miscellaneous", "misc expense", "other expense", "random expense",
        "postage", "courier", "delivery charge", "stamp duty",
        "notary", "legal fee", "fine", "penalty", "late fee",
        "subscription renewal", "annual fee", "membership fee",
        "gym fee", "club membership", "loyalty points",
    ],
}

# Flatten data
texts = []
labels = []

for cat, examples in CATEGORY_EXAMPLES.items():
    for ex in examples:
        texts.append(ex)
        labels.append(cat)

# Train vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)


# ============================================================
# PREDICT FUNCTION
# ============================================================
def predict_category(text):

    text_vec = vectorizer.transform([text])

    similarities = cosine_similarity(text_vec, X)[0]

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    predicted_category = labels[best_index]

    # Confidence threshold
    if best_score < 0.2:
        return "Others"

    return predicted_category