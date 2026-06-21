import os
import shutil
import glob

artifact_dir = "/Users/siavash/.gemini/antigravity/brain/fdaaad3a-10d7-4332-bb25-f26af40add74"
dest_dir = "/Users/siavash/Project/Lumia-Beauty-online-shop/backend/generated_images"

os.makedirs(dest_dir, exist_ok=True)

image_mapping = {
    "bleu_de_chanel": "bleu_de_chanel.png",
    "dior_sauvage": "dior_sauvage.png",
    "coco_mademoiselle": "coco_mademoiselle.png",
    "night_rose_lumia": "night_rose_lumia.png",
    "cerave_cleanser": "cerave_cleanser.png",
    "laneige_lip_mask": "laneige_lip_mask.png",
    "lumia_shampoo": "lumia_shampoo.png",
    "lumia_body_splash": "lumia_body_splash.png",
    "the_ordinary_hyaluronic": "the_ordinary_hyaluronic.png",
    "tom_ford_lost_cherry": "tom_ford_lost_cherry.png",
    "neutrogena_hydro_boost": "neutrogena_hydro_boost.png",
    "ogx_argan_oil": "ogx_argan_oil.png",
    "instagram_1": "instagram_1.png",
    "instagram_2": "instagram_2.png",
    "instagram_3": "instagram_3.png",
    "instagram_4": "instagram_4.png",
}

print("Starting to copy generated images...")
for prefix, target_name in image_mapping.items():
    pattern = os.path.join(artifact_dir, f"{prefix}_*.png")
    matches = glob.glob(pattern)
    if matches:
        # Sort to get the latest generated image if multiple exist
        matches.sort()
        src_path = matches[-1]
        dest_path = os.path.join(dest_dir, target_name)
        shutil.copy2(src_path, dest_path)
        print(f"Copied {os.path.basename(src_path)} -> {target_name}")
    else:
        print(f"No match found for prefix: {prefix}")

print("Image copy process finished.")
