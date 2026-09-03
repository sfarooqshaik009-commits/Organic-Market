import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "organic_market.settings",
)

import django

django.setup()

from store.models import Category, Product


PRODUCTS = {
    "vegetables": [
        (
            "Organic Tomato (Tamatar)",
            "Farm-fresh red juicy organic tomatoes.",
            40,
            "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Spinach (Palak)",
            "Fresh green leafy pesticide-free spinach.",
            25,
            "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Carrot (Gajar)",
            "Crunchy sweet organic orange carrots.",
            50,
            "https://images.unsplash.com/photo-1598170845058-12ef4a457939?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Broccoli",
            "Fresh nutrient-rich organic broccoli.",
            90,
            "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Cauliflower (Phool Gobhi)",
            "Fresh solid white organic cauliflower.",
            40,
            "https://images.unsplash.com/photo-1568584711075-3d021a7c3ca3?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Capsicum / Bell Pepper",
            "Crisp organic green bell pepper.",
            60,
            "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Cucumber (Kheera)",
            "Cool and hydrating organic cucumber.",
            30,
            "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Zucchini",
            "Fresh green organic zucchini.",
            80,
            "https://images.unsplash.com/photo-1588613254395-54e7d03a56df?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Eggplant (Brinjal / Baingan)",
            "Organic purple brinjal from local farms.",
            35,
            "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Radish (Mooli)",
            "Crisp organic white radish.",
            25,
            "https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Sweet Potato (Shakarkand)",
            "Naturally sweet organic root vegetable.",
            45,
            "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Beetroot",
            "Deep red fresh organic beetroots.",
            40,
            "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Garlic (Lahsun)",
            "Aromatic organic Indian garlic bulbs.",
            120,
            "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Red Onion (Pyaz)",
            "Fresh organic red onions.",
            35,
            "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cf?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Romaine Lettuce",
            "Crisp green organic lettuce leaves.",
            50,
            "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Asparagus",
            "Tender organic green asparagus stalks.",
            180,
            "https://images.unsplash.com/photo-1515471209610-e3f14d81e380?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Green Beans",
            "Fresh handpicked organic French beans.",
            60,
            "https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Cabbage (Patta Gobhi)",
            "Fresh solid green organic cabbage.",
            30,
            "https://images.unsplash.com/photo-1608219992759-8d74ed8d76eb?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Green Peas (Matar)",
            "Sweet fresh organic green peas.",
            70,
            "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Lady Finger (Bhindi)",
            "Tender organic okra / bhindi.",
            45,
            "https://images.unsplash.com/photo-1625944230945-1b7dd3b949ab?auto=format&fit=crop&w=500&q=80",
        ),
    ],

    "fruits": [
        (
            "Kashmiri Red Apple",
            "Sweet and crisp red apples from Kashmir.",
            160,
            "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Robusta Banana",
            "Naturally ripened sweet organic bananas.",
            50,
            "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Organic Strawberry",
            "Fresh juicy red strawberries.",
            180,
            "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Blueberry Pack",
            "Antioxidant-rich fresh blueberries.",
            250,
            "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Alphonso Mango",
            "Premium organic Alphonso mangoes.",
            350,
            "https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Nagpur Orange",
            "Juicy and sweet fresh Nagpur oranges.",
            80,
            "https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Pineapple",
            "Tropical sweet organic pineapple.",
            70,
            "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Butter Fruit (Avocado)",
            "Rich and creamy organic avocado.",
            150,
            "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Fresh Peach",
            "Juicy and sweet organic peaches.",
            140,
            "https://images.unsplash.com/photo-1595123550441-d377e017de6a?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Watermelon",
            "Refreshing organic watermelon.",
            60,
            "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Black Seedless Grapes",
            "Sweet organic seedless black grapes.",
            110,
            "https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Kiwi Fruit",
            "Tangy and vitamin C rich kiwi.",
            120,
            "https://images.unsplash.com/photo-1585059819970-31382223846a?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Pomegranate (Anar)",
            "Ruby red juicy organic pomegranate.",
            180,
            "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Papaya",
            "Fresh organic papaya.",
            50,
            "https://images.unsplash.com/photo-1517260739337-6799d239ce83?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Fresh Lemon (Nimbu)",
            "Zesty organic lemons.",
            40,
            "https://images.unsplash.com/photo-1534531141161-e41d133a4bfd?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Indian Plum",
            "Sweet organic red plums.",
            130,
            "https://images.unsplash.com/photo-1522184216316-3c25379f963c?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Cherry Pack",
            "Fresh sweet dark red cherries.",
            220,
            "https://images.unsplash.com/photo-1528825871115-3581a5387919?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Guava (Amrood)",
            "Crisp organic pink guava.",
            60,
            "https://images.unsplash.com/photo-1536511135764-00e2b17f8a7e?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Fresh Fig (Anjeer)",
            "Nutrient-packed organic fresh figs.",
            200,
            "https://images.unsplash.com/photo-1601379327928-1fed02888456?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Custard Apple (Sitaphal)",
            "Sweet creamy organic sitaphal.",
            140,
            "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=500&q=80",
        ),
    ],

    "fertilizers": [
        (
            "Vermicompost 5kg",
            "Pure organic earthworm castings for soil health.",
            250,
            "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Neem Cake Powder 1kg",
            "Natural pest deterrent and organic nitrogen booster.",
            120,
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Organic Cow Manure 5kg",
            "Aged and dried organic cow dung compost.",
            180,
            "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a81?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Bone Meal Powder 1kg",
            "High-phosphorus organic fertilizer.",
            150,
            "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Fish Amino Acid Liquid 500ml",
            "Fast-acting organic growth promoter.",
            290,
            "https://images.unsplash.com/photo-1516253593875-bd7ba052fbc5?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Bio-NPK Granules 1kg",
            "Balanced bacterial bio-fertilizer mix.",
            210,
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Seaweed Extract Liquid 250ml",
            "Organic micronutrient plant booster.",
            320,
            "https://images.unsplash.com/photo-1628352081506-83c43123ed6d?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Panchagavya Liquid 1L",
            "Traditional bio-fertilizer and growth tonic.",
            280,
            "https://images.unsplash.com/photo-1592417817098-8f3d6ef23a81?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Mustard Cake Powder 1kg",
            "Rich in nitrogen, potassium, and phosphorus.",
            95,
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=500&q=80",
        ),
        (
            "Epsom Salt for Plants 1kg",
            "Magnesium sulfate for green leaves and blooming.",
            110,
            "https://images.unsplash.com/photo-1615811361523-6bd03d7748e7?auto=format&fit=crop&w=500&q=80",
        ),
    ],
}


def run_seed():
    print("Starting Organic Market database seed...")

    Product.objects.all().delete()
    Category.objects.all().delete()

    total = 0

    for slug, items in PRODUCTS.items():
        category_name = slug.replace("-", " ").title()

        category = Category.objects.create(
            name=category_name,
            slug=slug,
        )

        for name, description, price, image in items:
            Product.objects.create(
                category=category,
                name=name,
                description=description,
                price=price,
                stock_qty=50,
                image=image,
                is_available=True,
            )
            total += 1

    print(f"Successfully created {total} products.")
    print("Database seed completed.")


if __name__ == "__main__":
    run_seed()