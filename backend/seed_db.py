import os
import sys
import django
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.catalog.models import Category, Brand, Product, ProductImage, ProductAttribute, Review, InstagramPost
from apps.blog.models import Post, PostCategory, Tag

User = get_user_model()

def create_mock_image(text, bg_color=(245, 240, 235), text_color=(139, 111, 92), size=(800, 800)):
    """Creates a mock product image with a solid background and centered text using Pillow."""
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Simple cross/border for decoration
    draw.rectangle([20, 20, size[0] - 20, size[1] - 20], outline=(201, 169, 110), width=2)
    draw.text((size[0]//2 - 100, size[1]//2 - 15), text, fill=text_color)
    
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return ContentFile(buffer.getvalue(), name=f"{text.replace(' ', '_')}.jpg")

def get_real_or_mock_image(filename, fallback_text, size=(800, 800)):
    """Loads a real generated image if it exists, otherwise falls back to a generated mock image."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    real_path = os.path.join(base_dir, "generated_images", filename)
    if os.path.exists(real_path):
        try:
            with open(real_path, "rb") as f:
                return ContentFile(f.read(), name=filename)
        except Exception as e:
            print(f"Error reading real image {filename}: {e}")
    # Fallback
    return create_mock_image(fallback_text, size=size)

def seed():
    print("Starting database seeding...")
    
    # 1. Create Superuser and Users
    superuser_phone = "09121111111"
    if not User.objects.filter(phone=superuser_phone).exists():
        admin_user = User.objects.create_superuser(phone=superuser_phone, password="password123")
        admin_user.first_name = "سیامک"
        admin_user.last_name = "امیری"
        admin_user.save()
        print("Superuser created (09121111111 / password123)")
    else:
        admin_user = User.objects.get(phone=superuser_phone)

    test_user_phone = "09122222222"
    if not User.objects.filter(phone=test_user_phone).exists():
        test_user = User.objects.create_user(phone=test_user_phone, password="password123")
        test_user.first_name = "سارا"
        test_user.last_name = "کریمی"
        test_user.save()
        print("Test user created (09122222222 / password123)")
    else:
        test_user = User.objects.get(phone=test_user_phone)

    # Add other mock users for reviews
    mock_users = []
    for i, name in enumerate([("مریم", "حسینی"), ("علی", "رضایی"), ("نازنین", "راد"), ("امیر", "سلیمانی")]):
        phone = f"0912333333{i}"
        if not User.objects.filter(phone=phone).exists():
            u = User.objects.create_user(phone=phone)
            u.first_name = name[0]
            u.last_name = name[1]
            u.save()
            mock_users.append(u)
        else:
            mock_users.append(User.objects.get(phone=phone))

    # 2. Create Categories
    # Clear existing to start clean
    Product.objects.all().delete()
    Category.objects.all().delete()
    Brand.objects.all().delete()
    PostCategory.objects.all().delete()
    Post.objects.all().delete()
    InstagramPost.objects.all().delete()
    Tag.objects.all().delete()

    print("Cleared existing categories, brands, products, blog posts, tags, and instagram posts.")

    # Perfumes Parent
    perfume_cat = Category.objects.create(name="خوشبوکننده‌ها", slug="fragrances", description="دنیای عطرهای اورجینال و لوکس")
    # Perfumes Children
    cool_perfume = Category.objects.create(name="عطرهای خنک", slug="cool-perfumes", mood="cool", parent=perfume_cat, sort_order=1)
    sweet_perfume = Category.objects.create(name="عطرهای شیرین", slug="sweet-perfumes", mood="sweet", parent=perfume_cat, sort_order=2)
    warm_perfume = Category.objects.create(name="عطرهای گرم", slug="warm-perfumes", mood="warm", parent=perfume_cat, sort_order=3)
    bitter_perfume = Category.objects.create(name="عطرهای تلخ", slug="bitter-perfumes", mood="bitter", parent=perfume_cat, sort_order=4)

    # Cosmetics Parent
    hygiene_cat = Category.objects.create(name="محصولات بهداشتی", slug="hygiene", description="بهترین محصولات مراقبتی برای پوست و مو")
    # Cosmetics Children
    hair_care = Category.objects.create(name="مراقبت مو", slug="hair-care", mood="haircare", parent=hygiene_cat, sort_order=1)
    skin_care = Category.objects.create(name="روتین پوست", slug="skin-care", mood="skincare", parent=hygiene_cat, sort_order=2)
    personal_hygiene = Category.objects.create(name="بهداشت شخصی", slug="personal-hygiene", mood="hygiene", parent=hygiene_cat, sort_order=3)

    print("Categories created.")

    # 3. Create Brands
    brand_lumia = Brand.objects.create(name="لومیا اسنس", slug="lumia-essence")
    brand_chanel = Brand.objects.create(name="شنل", slug="chanel")
    brand_dior = Brand.objects.create(name="دیور", slug="dior")
    brand_cerave = Brand.objects.create(name="سراوی", slug="cerave")
    brand_laneige = Brand.objects.create(name="لانیژ", slug="laneige")
    brand_the_ordinary = Brand.objects.create(name="دی اوردینری", slug="the-ordinary")
    brand_tom_ford = Brand.objects.create(name="تام فورد", slug="tom-ford")
    brand_neutrogena = Brand.objects.create(name="نوتروژینا", slug="neutrogena")
    brand_ogx = Brand.objects.create(name="او جی ایکس", slug="ogx")

    print("Brands created.")

    # 4. Create Products
    products_data = [
        # Fragrances
        {
            "name": "عطر بلو شنل مردانه",
            "slug": "bleu-de-chanel",
            "image_name": "bleu_de_chanel.png",
            "description": "عطر ادکلن بلو شنل ادو پرفیوم عطر مردانه شیک و باوقار، با رایحه تلخ و خنک که برای فصول گرم سال و جلسات رسمی ایده‌آل است. نت‌های بویایی این عطر شامل گریپ‌فروت، لیمو، نعناع، جوز هندی و صندل سفید است.",
            "short_description": "عطر ادکلن مردانه با رایحه تلخ و خنک و ماندگاری بالا با ضمانت اصالت",
            "category": cool_perfume,
            "brand": brand_chanel,
            "price": 4800000,
            "compare_at_price": 5300000,
            "stock": 15,
            "sku": "CH-BL-01",
            "is_featured": True,
            "attributes": [
                ("volume", "۱۰۰ میلی‌لیتر"),
                ("scent", "خنک و تلخ چوبی مرکباتی"),
                ("product_type", "ادو پرفیوم")
            ],
            "reviews": [
                {"user": mock_users[0], "rating": 5, "comment": "رایحه فوق‌العاده باکلاس و شیکی داره. پخش بوش هم عالیه."},
                {"user": mock_users[1], "rating": 4, "comment": "عطر خنک و باوقاری هست ولی برای زمستون شاید مناسب نباشه. در کل راضیم."}
            ]
        },
        {
            "name": "عطر دیور ساواج ادو پرفیوم",
            "slug": "dior-sauvage",
            "image_name": "dior_sauvage.png",
            "description": "دیور ساوج ادو پرفیوم عطری سلطنتی و جذاب برای آقایان شیک‌پوش. رایحه‌ای معتدل رو به گرم دارد که از ترکیب ترنج کالابریا، فلفل سیچوان، اسطوخودوس، انیسون ستاره‌ای و جوز هندی تشکیل شده و حس حضور در صحرا در غروب آفتاب را تداعی می‌کند.",
            "short_description": "عطر سلطنتی و همه‌پسند مردانه با پخش بوی فوق‌العاده",
            "category": warm_perfume,
            "brand": brand_dior,
            "price": 5200000,
            "compare_at_price": None,
            "stock": 8,
            "sku": "DI-SA-02",
            "is_featured": True,
            "attributes": [
                ("volume", "۱۰۰ میلی‌لیتر"),
                ("scent", "تند و معتدل رو به گرم چوبی"),
                ("product_type", "ادو پرفیوم")
            ],
            "reviews": [
                {"user": mock_users[2], "rating": 5, "comment": "بهترین عطری که تا حالا خریدم. همه جا اسمشو ازم می‌پرسن!"}
            ]
        },
        {
            "name": "عطر کوکو مادمازل شنل زنانه",
            "slug": "coco-mademoiselle",
            "image_name": "coco_mademoiselle.png",
            "description": "شنل کوکو مادمازل عطری ملایم و شیرین است که نماد یک زن آزاد و فریبنده است. نتهای آغازین پرتقال، ترنج و گریپ فروت هستند؛ نت‌های میانی رز، یاسمن و سرخالو؛ و نتهای پایانی نعناع هندی، خس خس، وانیل و مشک می‌باشند.",
            "short_description": "عطر زنانه ملایم و شیرین، نماد وقار و زیبایی زنانه",
            "category": sweet_perfume,
            "brand": brand_chanel,
            "price": 6100000,
            "compare_at_price": 6500000,
            "stock": 5,
            "sku": "CH-CO-03",
            "is_featured": True,
            "attributes": [
                ("volume", "۱۰۰ میلی‌لیتر"),
                ("scent", "ملایم و شیرین گلی مدیترانه‌ای"),
                ("product_type", "ادو پرفیوم")
            ],
            "reviews": [
                {"user": mock_users[3], "rating": 5, "comment": "امضای منه این عطر. بوی گل سرخ و مرکباتش بی‌نظیره."}
            ]
        },
        {
            "name": "عطر لومیا اسنس نایت رز",
            "slug": "lumia-essence-night-rose",
            "image_name": "night_rose_lumia.png",
            "description": "عطر لومیا اسنس مدل نایت رز رایحه‌ای تلخ و گرم دارد که برای شب‌های سرد پاییز و زمستان طراحی شده است. رایحه میانی این عطر را بوی رز سیاه و چرم تشکیل داده است که ماندگاری بیش از ۲۴ ساعت را تضمین می‌کند.",
            "short_description": "عطر نیش با رایحه گرم و تلخ، با دوام فوق‌العاده شبانه",
            "category": bitter_perfume,
            "brand": brand_lumia,
            "price": 2800000,
            "compare_at_price": 3200000,
            "stock": 20,
            "sku": "LE-NR-04",
            "is_featured": False,
            "attributes": [
                ("volume", "۸۰ میلی‌لیتر"),
                ("scent", "گرم و تلخ رز و چرمی"),
                ("product_type", "ادو پرفیوم")
            ],
            "reviews": []
        },
        {
            "name": "عطر تام فورد لاست چری",
            "slug": "tom-ford-lost-cherry",
            "image_name": "tom_ford_lost_cherry.png",
            "description": "عطر ادکلن تام فورد لاست چری ادو پرفیوم زنانه و مردانه با رایحه‌ای مجلل، شیرین و گرم از آلبالو، بادام تلخ، لیکور، آلو، یاس و صندل سفید. عطری بسیار خاص پسند، لوکس و نیش با ماندگاری و خط بوی استثنایی.",
            "short_description": "عطر ادکلن نیش زنانه و مردانه تام فورد لاست چری اصل با خط بوی عالی",
            "category": sweet_perfume,
            "brand": brand_tom_ford,
            "price": 7500000,
            "compare_at_price": 8200000,
            "stock": 4,
            "sku": "TF-LC-09",
            "is_featured": True,
            "attributes": [
                ("volume", "۱۰۰ میلی‌لیتر"),
                ("scent", "شیرین و گرم گلی میوه‌ای"),
                ("product_type", "ادو پرفیوم")
            ],
            "reviews": [
                {"user": mock_users[1], "rating": 5, "comment": "عجب بوی آلبالوی نابی داره! فوق العاده شیک و گرون‌قیمته."}
            ]
        },
        
        # Skin Care / Hygiene
        {
            "name": "ژل شستشوی آبرسان سراوی",
            "slug": "cerave-hydrating-cleanser",
            "image_name": "cerave_cleanser.png",
            "description": "ژل شستشوی آبرسان سراوی برای پوست‌های نرمال تا خشک توسعه یافته است. این محصول با داشتن ۳ سرامید ضروری پوست و هیالورونیک اسید، کثیفی و چربی را پاک کرده و همزمان رطوبت طبیعی پوست را بدون آسیب به سد دفاعی حفظ می‌کند.",
            "short_description": "شوینده ملایم و آبرسان پوست خشک تا نرمال فاقد صابون",
            "category": skin_care,
            "brand": brand_cerave,
            "price": 950000,
            "compare_at_price": 1100000,
            "stock": 35,
            "sku": "CE-HC-05",
            "is_featured": True,
            "attributes": [
                ("volume", "۲۳۶ میلی‌لیتر"),
                ("skin_type", "پوست خشک، حساس و نرمال"),
                ("product_type", "شوینده صورت")
            ],
            "reviews": [
                {"user": mock_users[0], "rating": 5, "comment": "برای پوست خشک من معجزه کرد. اصلاً پوست رو کشیده و خشک نمی‌کنه بعد شستشو."}
            ]
        },
        {
            "name": "ماسک خواب لب لانیژ طعم توت فرنگی",
            "slug": "laneige-lip-sleeping-mask",
            "image_name": "laneige_lip_mask.png",
            "description": "ماسک خواب لب لانیژ لب‌های شما را در طول شب مرطوب و تغذیه می‌کند. این محصول با استفاده از فناوری اختصاصی Moisture Wrap و غنی از ویتامین C و آنتی‌اکسیدان‌ها، لب‌های خشک و پوسته‌پوسته شده را نرم و لطیف می‌کند.",
            "short_description": "ماسک لب شبانه لانیژ جهت رفع خشکی و ایجاد لطافت لب‌ها",
            "category": skin_care,
            "brand": brand_laneige,
            "price": 680000,
            "compare_at_price": 750000,
            "stock": 40,
            "sku": "LA-LM-06",
            "is_featured": True,
            "attributes": [
                ("volume", "۲۰ گرم"),
                ("skin_type", "انواع لب‌ها"),
                ("product_type", "ماسک لب")
            ],
            "reviews": [
                {"user": mock_users[2], "rating": 5, "comment": "شب می‌زنم و صبح که بیدار می‌شم لب‌هام کاملاً نرم و صورتی هستن. عالیه."}
            ]
        },
        {
            "name": "شامپو بدون سولفات لومیا برای موهای آسیب‌دیده",
            "slug": "lumia-sulfate-free-shampoo",
            "image_name": "lumia_shampoo.png",
            "description": "شامپو بدون سولفات لومیا فرمولاسیونی ملایم و ارگانیک دارد که با پروتئین هیدرولیز شده کراتین و روغن آرگان غنی شده است. این شامپو موهای وز و رنگ‌شده را بازسازی کرده و درخشش طبیعی به موها می‌بخشد.",
            "short_description": "شامپوی ملایم بدون سولفات تقویت‌کننده و محافظ رنگ مو",
            "category": hair_care,
            "brand": brand_lumia,
            "price": 320000,
            "compare_at_price": None,
            "stock": 50,
            "sku": "LE-SS-07",
            "is_featured": False,
            "attributes": [
                ("volume", "۴۰۰ میلی‌لیتر"),
                ("skin_type", "موهای کراتینه، رنگ شده و خشک"),
                ("product_type", "شامپو")
            ],
            "reviews": []
        },
        {
            "name": "بادی اسپلش لومیا رایحه وانیل و ارکیده",
            "slug": "lumia-body-splash-vanilla",
            "image_name": "lumia_body_splash.png",
            "description": "بادی اسپلش لومیا بیوتی با رایحه شیرین و ملایم وانیل و شکوفه ارکیده، حس تازگی و طراوت بعد از حمام را به پوست شما می‌بخشد. حاوی آلوئه‌ورا و بابونه جهت نرم‌کنندگی پوست بدن.",
            "short_description": "بادی اسپلش خوشبوکننده بدن با ماندگاری خوب و خاصیت نرم‌کنندگی",
            "category": personal_hygiene,
            "brand": brand_lumia,
            "price": 450000,
            "compare_at_price": 500000,
            "stock": 30,
            "sku": "LE-BS-08",
            "is_featured": False,
            "attributes": [
                ("volume", "۲۵۰ میلی‌لیتر"),
                ("skin_type", "انواع پوست"),
                ("product_type", "خوشبوکننده بدن")
            ],
            "reviews": []
        },
        {
            "name": "سرم آبرسان هیالورونیک اسید دی اوردینری",
            "slug": "the-ordinary-hyaluronic-acid",
            "image_name": "the_ordinary_hyaluronic.png",
            "description": "سرم آبرسان بسیار قوی هیالورونیک اسید ۲٪ + B5 دی اوردینری. این سرم حاوی سه وزن مولکولی مختلف هیالورونیک اسید برای نفوذ عمیق به لایه‌های مختلف پوست و همچنین ویتامین B5 جهت بازسازی سد دفاعی پوست می‌باشد. فاقد پارابن، الکل و سیلیکون.",
            "short_description": "سرم آبرسان عمیق و جوانساز هیالورونیک اسید اوردینری اصل",
            "category": skin_care,
            "brand": brand_the_ordinary,
            "price": 850000,
            "compare_at_price": 950000,
            "stock": 25,
            "sku": "TO-HA-10",
            "is_featured": True,
            "attributes": [
                ("volume", "۳۰ میلی‌لیتر"),
                ("skin_type", "انواع پوست بخصوص دهیتراته"),
                ("product_type", "سرم پوست")
            ],
            "reviews": [
                {"user": mock_users[3], "rating": 5, "comment": "عالیه! بعد از چند روز استفاده پوست شاداب‌تر و پرتر به نظر می‌رسه."}
            ]
        },
        {
            "name": "کرم واتر ژل آبرسان نوتروژینا مدل هیدرو بوست",
            "slug": "neutrogena-hydro-boost-water-gel",
            "image_name": "neutrogena_hydro_boost.png",
            "description": "واتر ژل آبرسان هیدرو بوست نوتروژینا (Neutrogena Hydro Boost Water Gel) با فرمولاسیونی غنی از هیالورونیک اسید، پوست را به طور مداوم و در طول روز آبرسانی می‌کند. بافتی فوق‌العاده سبک، ژلی و فاقد چربی دارد که بلافاصله جذب شده و پوست را شاداب و مات نگه می‌دارد.",
            "short_description": "ژل کرم آبرسان و مرطوب کننده هیدرو بوست نوتروژینا اصل فاقد چربی",
            "category": skin_care,
            "brand": brand_neutrogena,
            "price": 620000,
            "compare_at_price": 690000,
            "stock": 18,
            "sku": "NE-HB-11",
            "is_featured": True,
            "attributes": [
                ("volume", "۵۰ میلی‌لیتر"),
                ("skin_type", "پوست‌های چرب، مختلط و دهیتراته"),
                ("product_type", "آبرسان صورت")
            ],
            "reviews": []
        },
        {
            "name": "روغن آرگان خالص مراکشی او جی ایکس",
            "slug": "ogx-argan-oil-of-morocco",
            "image_name": "ogx_argan_oil.png",
            "description": "روغن آرگان Renewing + Argan Oil of Morocco برند او جی ایکس (OGX). فرمولاسیونی گرانبها و غنی از روغن آرگان مراکش جهت احیا، نرم‌کنندگی و بازسازی کامل موهای خشک، وز و آسیب‌دیده. افزایش خیره‌کننده درخشش و مقاومت تارهای مو در برابر حرارت.",
            "short_description": "روغن آرگان مراکشی او جی ایکس تقویت‌کننده و درخشان‌کننده مو اصل",
            "category": hair_care,
            "brand": brand_ogx,
            "price": 780000,
            "compare_at_price": None,
            "stock": 20,
            "sku": "OG-AO-12",
            "is_featured": False,
            "attributes": [
                ("volume", "۱۰۰ میلی‌لیتر"),
                ("skin_type", "موهای خشک، وز و آسیب‌دیده"),
                ("product_type", "روغن مو")
            ],
            "reviews": []
        }
    ]

    for p_data in products_data:
        p = Product.objects.create(
            name=p_data["name"],
            slug=p_data["slug"],
            description=p_data["description"],
            short_description=p_data["short_description"],
            category=p_data["category"],
            brand=p_data["brand"],
            price=p_data["price"],
            compare_at_price=p_data["compare_at_price"],
            stock=p_data["stock"],
            sku=p_data["sku"],
            is_featured=p_data["is_featured"]
        )
        
        # Save mock product images (primary and gallery)
        img_content = get_real_or_mock_image(p_data["image_name"], p_data["name"])
        ProductImage.objects.create(product=p, image=img_content, alt_text=p_data["name"], is_primary=True, sort_order=0)
        
        # Additional gallery image (fallback or mock)
        img_content_2 = create_mock_image(f"{p_data['name']} - زاویه دیگر", bg_color=(240, 245, 245))
        ProductImage.objects.create(product=p, image=img_content_2, alt_text=f"{p_data['name']} gallery", is_primary=False, sort_order=1)

        # Attributes
        for attr_key, attr_val in p_data["attributes"]:
            ProductAttribute.objects.create(product=p, key=attr_key, value=attr_val)
            
        # Reviews
        for rev in p_data["reviews"]:
            Review.objects.create(product=p, user=rev["user"], rating=rev["rating"], comment=rev["comment"], is_approved=True)

    print("Products and ProductImages and Reviews created.")

    # 5. Create Instagram Posts
    ig_posts = [
        {"url": "https://www.instagram.com/p/C_beauty1", "caption": "روتین مراقبت شبانه با محصولات لانیژ و سراوی"},
        {"url": "https://www.instagram.com/p/C_beauty2", "caption": "رایحه‌ای که امضای توست؛ معرفی ادکلن بلو شنل اورجینال"},
        {"url": "https://www.instagram.com/p/C_beauty3", "caption": "پک ویژه کادو عید وانیل و رز سیاه Lumia Essence"},
        {"url": "https://www.instagram.com/p/C_beauty4", "caption": "رضایت مشتریان عزیز از مشاوره رایگان انتخاب عطر ما"}
    ]
    
    for i, post in enumerate(ig_posts):
        img_filename = f"instagram_{i+1}.png"
        img_content = get_real_or_mock_image(img_filename, f"اینستاگرام {i+1}", size=(600, 600))
        InstagramPost.objects.create(
            image=img_content,
            post_url=post["url"],
            caption=post["caption"],
            sort_order=i,
            is_active=True
        )
    print("Instagram mock posts created.")

    # 6. Create Blog Categories and Posts
    blog_cat_skin = PostCategory.objects.create(name="مراقبت پوست", slug="skin-care-blog")
    blog_cat_perfume = PostCategory.objects.create(name="عطرشناسی", slug="perfumery")
    
    tag_routine = Tag.objects.create(name="روتین", slug="routine")
    tag_summer = Tag.objects.create(name="تابستان", slug="summer")
    
    # Post 1
    post1 = Post.objects.create(
        title="۱۰ قدم ساده برای داشتن روتین پوست چرب و بدون جوش",
        slug="oily-skin-routine-10-steps",
        excerpt="داشتن پوست چرب گاهی چالش‌برانگیز است، اما با یک روتین منظم و استفاده از محصولات مناسب می‌توانید چربی پوست را کنترل کرده و از جوش زدن جلوگیری کنید. در این مقاله ۱۰ گام طلایی را با هم مرور می‌کنیم...",
        content="""داشتن پوست چرب به معنای فعالیت بیش از حد غدد چربی (سبوم) است. این موضوع می‌تواند منجر به مسدود شدن منافذ پوست و در نهایت جوش و آکنه شود. اما نگران نباشید! با داشتن یک روتین روزانه اصولی می‌توانید پوستی شاداب، مات و بدون جوش داشته باشید.

گام ۱: پاک‌سازی ملایم دو بار در روز
پاک کردن صورت صبح و شب با یک شوینده ملایم حاوی سالیسیلیک اسید یا سرامید اولین و مهم‌ترین قدم است. شوینده‌های خشن چربی طبیعی پوست را کاملاً از بین می‌برند که باعث تولید چربی جبرانی بیشتر می‌شود.

گام ۲: استفاده از تونر کنترل‌کننده چربی
تونرها به تنظیم pH پوست کمک کرده و باقی‌مانده آلودگی‌ها را پاک می‌کنند.

گام ۳: مرطوب‌کننده فاقد چربی (Oil-Free)
بزرگترین اشتباه افراد دارای پوست چرب، حذف مرطوب‌کننده است. پوست بی‌آب چربی بیشتری ترشح می‌کند. از کرم‌های ژلی و سبک استفاده کنید.

گام ۴: ضدآفتاب مات‌کننده فیزیکی
ضدآفتاب‌های فلوئیدی و فاقد چربی بهترین انتخاب هستند تا منافذ شما مسدود نشوند.

این روتین ساده اما مداوم، شادابی و سلامت پوست شما را به شدت افزایش می‌دهد. محصولات مناسب پوست خود را می‌توانید در بخش روتین پوست فروشگاه لومیا بیوتی تهیه کنید.""",
        category=blog_cat_skin,
        author=admin_user,
        is_published=True,
        meta_title="روتین پوست چرب و جوش دار — لومیا بیوتی",
        meta_description="راهنمای جامع ۱۰ قدمی برای مراقبت از پوست چرب، کنترل ترشح چربی و پیشگیری از جوش‌های سرسیاه و آکنه با محصولات ارگانیک.",
        published_at=django.utils.timezone.now()
    )
    post1.tags.add(tag_routine)
    img_content = get_real_or_mock_image("blog_skin_care.png", "مقاله روتین پوست چرب", size=(900, 500))
    post1.cover_image = img_content
    post1.save()

    # Post 2
    post2 = Post.objects.create(
        title="چگونه عطر مناسب فصل تابستان را انتخاب کنیم؟ راهنمای نت‌های بویایی",
        slug="how-to-choose-summer-perfume",
        excerpt="انتخاب عطر در فصل تابستان به دلیل گرمای هوا و تبخیر سریع عطر اهمیت زیادی دارد. عطرهای خنک، مرکباتی و دریایی بهترین گزینه‌ها برای روزهای گرم هستند. با راهنمای ما بهترین انتخاب را داشته باشید...",
        content="""فصل تابستان فصل گرما، انرژی و فعالیت‌های بیرونی است. با افزایش دمای هوا، عطرهایی که استفاده می‌کنیم نیز سریع‌تر تبخیر می‌شوند و پخش بوی بیشتری پیدا می‌کنند. بنابراین عطرهای گرم و شیرین زمستانه در تابستان می‌توانند بیش از حد سنگین و آزاردهنده باشند.

در این مقاله راهنمای کاملی برای خرید عطر تابستانی ارائه می‌دهیم:

۱. به دنبال نت‌های مرکباتی باشید
نت‌های لیمو، گریپ‌فروت، ترنج و پرتقال حس تازگی و خنکی فوق‌العاده‌ای در ابتدای اسپری عطر ایجاد می‌کنند. عطر بلو شنل نمونه بارزی از این نت‌هاست.

۲. نت‌های دریایی و اقیانوسی
رایحه نمک دریا، جلبک‌های دریایی و آب خنک حس ساحل و اقیانوس را شبیه‌سازی کرده و بسیار سبک و باطراوت هستند.

۳. نت‌های سبز و گیاهی
بوی نعناع، چای سبز، ریحان و برگ درختان حس تمیزی و سرزندگی طبیعت را منتقل می‌کنند.

برای تابستان ادوتویلت‌ها و ادوکلن‌ها به دلیل سبکی گزینه‌های مناسب‌تری برای مصرف روزانه هستند. می‌توانید عطرهای تابستانه خود را با ضمانت اصالت از لومیا بیوتی تهیه کنید.""",
        category=blog_cat_perfume,
        author=admin_user,
        is_published=True,
        meta_title="راهنمای خرید عطر تابستانه مردانه و زنانه — لومیا بیوتی",
        meta_description="چطور در تابستان بهترین عطر خنک و مرکباتی را انتخاب کنیم؟ بررسی کامل نت‌های بویایی دریایی و گیاهی عطرها.",
        published_at=django.utils.timezone.now()
    )
    post2.tags.add(tag_summer, tag_routine)
    img_content = get_real_or_mock_image("blog_summer_perfume.png", "مقاله عطر تابستانه", size=(900, 500))
    post2.cover_image = img_content
    post2.save()

    print("Blog articles created.")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
