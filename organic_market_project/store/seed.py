import os
import sys
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'organic_market.settings')

import django
django.setup()

from store.models import Category, Product

def run_seed():
    print("Clearing existing products...")
    Product.objects.all().delete()
    Category.objects.all().delete()

    print("Creating categories...")
    fruits_cat = Category.objects.create(name="Fruits", slug="fruits", description="Fresh organic fruits")
    veg_cat = Category.objects.create(name="Vegetables", slug="vegetables", description="Farm-fresh organic vegetables")
    fert_cat = Category.objects.create(name="Fertilizers", slug="fertilizers", description="100% bio & organic fertilizers")

    print("Seeding 20 Vegetables, 20 Fruits, and 20 Fertilizers with Indian Pricing (₹)...")

    # 20 VEGETABLES
    veggies = [
        ("Organic Tomato (Tamatar)", "organic-tomato", "Farm-fresh red juicy organic tomatoes.", 40.00, "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=500&q=80"),
        ("Spinach (Palak)", "spinach-palak", "Fresh green leafy pesticide-free spinach.", 25.00, "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=500&q=80"),
        ("Carrot (Gajar)", "carrot-gajar", "Crunchy sweet organic orange carrots.", 50.00, "https://images.unsplash.com/photo-1598170845058-12ef4a457939?auto=format&fit=crop&w=500&q=80"),
        ("Broccoli", "broccoli", "Fresh nutrient-rich organic broccoli head.", 90.00, "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&w=500&q=80"),
        ("Cauliflower (Phool Gobhi)", "cauliflower", "Fresh solid white organic cauliflower.", 40.00, "https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?auto=format&fit=crop&w=500&q=80"),
        ("Capsicum / Bell Pepper", "capsicum", "Crisp green organic bell pepper.", 60.00, "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=500&q=80"),
        ("Cucumber (Kheera)", "cucumber-kheera", "Cool and hydrating organic cucumber.", 30.00, "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=500&q=80"),
        ("Zucchini", "zucchini", "Fresh green organic zucchini.", 80.00, "https://images.unsplash.com/photo-1588613254395-54e7d03a56df?auto=format&fit=crop&w=500&q=80"),
        ("Eggplant (Brinjal / Baingan)", "brinjal-baingan", "Organic purple brinjal from local farms.", 35.00, "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=500&q=80"),
        ("Radish (Mooli)", "radish-mooli", "Crisp organic white radish.", 25.00, "https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?auto=format&fit=crop&w=500&q=80"),
        ("Sweet Potato (Shakarkand)", "sweet-potato", "Naturally sweet organic root vegetable.", 45.00, "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=500&q=80"),
        ("Beetroot", "beetroot", "Deep red fresh organic beetroots.", 40.00, "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=500&q=80"),
        ("Garlic (Lahsun)", "garlic-lahsun", "Aromatic organic Indian garlic bulbs.", 120.00, "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?auto=format&fit=crop&w=500&q=80"),
        ("Red Onion (Pyaz)", "red-onion", "Fresh organic red onions.", 35.00, "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cf?auto=format&fit=crop&w=500&q=80"),
        ("Romaine Lettuce", "romaine-lettuce", "Crisp green organic lettuce leaves.", 50.00, "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&w=500&q=80"),
        ("Asparagus", "asparagus", "Tender organic green asparagus stalks.", 180.00, "https://images.unsplash.com/photo-1515471209610-e3f14d81e380?auto=format&fit=crop&w=500&q=80"),
        ("Green Beans", "green-beans", "Fresh handpicked organic French beans.", 60.00, "https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?auto=format&fit=crop&w=500&q=80"),
        ("Cabbage (Patta Gobhi)", "cabbage-patta-gobhi", "Fresh solid green organic cabbage.", 30.00, "https://images.unsplash.com/photo-1608219992759-8d74ed8d76eb?auto=format&fit=crop&w=500&q=80"),
        ("Green Peas (Matar)", "green-peas-matar", "Sweet fresh organic green peas.", 70.00, "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=500&q=80"),
        ("Lady Finger (Bhindi)", "lady-finger-bhindi", "Tender organic okra / bhindi.", 45.00, "https://images.unsplash.com/photo-1625944230945-1b7dd3b949ab?auto=format&fit=crop&w=500&q=80")
    ]

    # 20 FRUITS
    fruits = [
        ("Kashmiri Red Apple", "kashmiri-red-apple", "Sweet and crisp red apples from Kashmir.", 160.00, "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=500&q=80"),
        ("Robusta Banana", "robusta-banana", "Naturally ripened sweet organic bananas.", 50.00, "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=500&q=80"),
        ("Organic Strawberry", "organic-strawberry", "Fresh juicy red strawberries.", 180.00, "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=500&q=80"),
        ("Blueberry Pack", "blueberry-pack", "Antioxidant-rich fresh blueberries.", 250.00, "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&w=500&q=80"),
        ("Alphonso Mango", "alphonso-mango", "King of mangoes, premium organic Alphonso.", 350.00, "https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=500&q=80"),
        ("Nagpur Orange", "nagpur-orange", "Juicy and sweet fresh Nagpur oranges.", 80.00, "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=500&q=80"),
        ("Pineapple", "pineapple", "Tropical sweet organic pineapple.", 70.00, "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&w=500&q=80"),
        ("Butter Fruit (Avocado)", "butter-fruit-avocado", "Rich and creamy organic avocado.", 150.00, "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&w=500&q=80"),
        ("Fresh Peach", "fresh-peach", "Juicy and sweet organic peaches.", 140.00, "https://images.unsplash.com/photo-1595123550441-d377e017de6a?auto=format&fit=crop&w=500&q=80"),
        ("Watermelon", "watermelon", "Refreshing water-rich organic watermelon.", 60.00, "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=500&q=80"),
        ("Black Seedless Grapes", "black-grapes", "Sweet organic seedless black grapes.", 110.00, "https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&w=500&q=80"),
        ("Kiwi Fruit", "kiwi-fruit", "Tangy and vitamin C rich kiwi.", 120.00, "https://images.unsplash.com/photo-1585059819970-31382223846a?auto=format&fit=crop&w=500&q=80"),
        ("Pomegranate (Anar)", "pomegranate-anar", "Ruby red juicy organic pomegranate.", 180.00, "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=500&q=80"),
        ("Papaya", "papaya", "Fresh digestion-friendly organic papaya.", 50.00, "https://images.unsplash.com/photo-1517260739337-6799d239ce83?auto=format&fit=crop&w=500&q=80"),
        ("Fresh Lemon (Nimbu)", "fresh-lemon", "Zesty organic lemons.", 40.00, "https://images.unsplash.com/photo-1534531141161-e41d133a4bfd?auto=format&fit=crop&w=500&q=80"),
        ("Indian Plum", "indian-plum", "Sweet organic red plums.", 130.00, "https://images.unsplash.com/photo-1522184216316-3c25379f963c?auto=format&fit=crop&w=500&q=80"),
        ("Cherry Pack", "cherry-pack", "Fresh sweet dark red cherries.", 220.00, "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=500&q=80"),
        ("Guava (Amrood)", "guava-amrood", "Crisp organic pink guava.", 60.00, "https://images.unsplash.com/photo-1536511135764-00e2b17f8a7e?auto=format&fit=crop&w=500&q=80"),
        ("Fresh Fig (Anjeer)", "fresh-fig-anjeer", "Nutrient-packed organic fresh figs.", 200.00, "https://images.unsplash.com/photo-1601379327928-1fed02888456?auto=format&fit=crop&w=500&q=80"),
        ("Custard Apple (Sitaphal)", "custard-apple", "Sweet creamy organic sitaphal.", 140.00, "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=500&q=80")
    ]

    # 20 FERTILIZERS
    fertilizers = [
        ("Vermicompost 5kg", "vermicompost-5kg", "Pure organic earthworm castings for soil health.", 250.00, "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80"),
        ("Neem Cake Powder 1kg", "neem-cake-powder", "Natural pest deterrent and organic nitrogen booster.", 120.00, "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80"),
        ("Organic Cow Manure 5kg", "cow-manure-5kg", "Aged and dried organic cow dung compost.", 180.00, "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a81?auto=format&fit=crop&w=500&q=80"),
        ("Bone Meal Powder 1kg", "bone-meal-1kg", "High-phosphorus organic fertilizer for flowering & roots.", 150.00, "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?auto=format&fit=crop&w=500&q=80"),
        ("Fish Amino Acid Liquid 500ml", "fish-amino-acid", "Fast-acting organic growth promoter for all plants.", 290.00, "https://images.unsplash.com/photo-1516253593875-bd7ba052fbc5?auto=format&fit=crop&w=500&q=80"),
        ("Bio-NPK Granules 1kg", "bio-npk-granules", "Balanced bacterial bio-fertilizer mix.", 210.00, "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80"),
        ("Seaweed Extract Liquid 250ml", "seaweed-extract", "100% organic micronutrient plant booster.", 320.00, "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80"),
        ("Panchagavya Liquid 1L", "panchagavya-1l", "Traditional Vedic bio-fertilizer and growth tonic.", 280.00, "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a81?auto=format&fit=crop&w=500&q=80"),
        ("Mustard Cake Powder 1kg", "mustard-cake", "Rich in nitrogen, potassium, and phosphorus.", 95.00, "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80"),
        ("Epsom Salt for Plants 1kg", "epsom-salt", "Magnesium sulfate for green leaves & blooming.", 110.00, "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?auto=format&fit=crop&w=500&q=80"),
        ("Humic Acid Flakes 500g", "humic-acid", "Concentrated soil conditioner for root expansion.", 240.00, "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80"),
        ("Trichoderma Viride Bio-Fungicide", "trichoderma-viride", "Organic defense against soil-borne root diseases.", 190.00, "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80"),
        ("Pseudomonas Fluorescens 1kg", "pseudomonas", "Bio-pesticide and plant growth stimulator.", 180.00, "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?auto=format&fit=crop&w=500&q=80"),
        ("Cocopeat Block 5kg", "cocopeat-block", "100% natural coconut husk substrate for moisture.", 220.00, "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a81?auto=format&fit=crop&w=500&q=80"),
        ("Steamed Bone Meal 1kg", "steamed-bone-meal", "Slow-release phosphorus and calcium for plants.", 160.00, "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80"),
        ("Rock Phosphate Powder 1kg", "rock-phosphate", "Natural mineral source for flowering and fruiting.", 130.00, "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80"),
        ("Organic Potting Soil Mix 5kg", "potting-soil-mix", "Ready-to-use enriched garden potting media.", 299.00, "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a81?auto=format&fit=crop&w=500&q=80"),
        ("Bio Zyme Fertilizer 1kg", "bio-zyme", "Organic enzyme-based soil energizer.", 210.00, "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?auto=format&fit=crop&w=500&q=80"),
        ("Perlite for Gardening 1kg", "perlite-1kg", "Volcanic glass perlite for soil aeration.", 175.00, "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80"),
        ("Mycorrhizal Bio-Fertilizer 250g", "mycorrhizal-bio", "Beneficial root fungi for max nutrient absorption.", 350.00, "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80")
    ]

    for name, slug, desc, price, img in veggies:
        Product.objects.create(category=veg_cat, name=name, slug=slug, description=desc, price=price, stock=50, image_url=img)

    for name, slug, desc, price, img in fruits:
        Product.objects.create(category=fruits_cat, name=name, slug=slug, description=desc, price=price, stock=50, image_url=img)

    for name, slug, desc, price, img in fertilizers:
        Product.objects.create(category=fert_cat, name=name, slug=slug, description=desc, price=price, stock=50, image_url=img)

    print("Success! Database seeded with 60 products with Indian Rupees (₹) prices.")

if __name__ == "__main__":
    run_seed()