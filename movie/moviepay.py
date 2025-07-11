import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 🔒 Ne pas utiliser ImageMagick
os.environ["IMAGE_MAGICK_BINARY"] = "None"

# ✅ Patch Pillow (compatibilité Pillow >= 10)
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.video.VideoClip import ImageClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import concatenate_videoclips

# --- PARAMÈTRES ---
IMG_DIR = "image"
MUSIC_FILE = os.path.join("music", "african_soft_music.mp3")
FONT_NAME = os.path.join("fonts", "OpenSans-Bold.ttf")
if not os.path.exists(FONT_NAME):
    print(f"⚠️ Le fichier de police '{FONT_NAME}' est introuvable.")

# --- FONCTION POUR GÉNÉRER LE TEXTE ---
def create_text_image(text, font_size=52, font_color="white", stroke_width=2,
                      stroke_color="black", font_name="arial.ttf", image_size=(1280, 200),
                      max_font_size=52, min_font_size=20):

    img = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    current_size = max_font_size
    wrapped_text = text
    while current_size >= min_font_size:
        try:
            font = ImageFont.truetype(font_name, current_size)
        except OSError:
            font = ImageFont.load_default()

        lines = textwrap.wrap(text, width=40)
        wrapped_text = "\n".join(lines)

        text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=4, stroke_width=stroke_width)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        if text_width <= image_size[0] - 40 and text_height <= image_size[1] - 20:
            break
        current_size -= 2

    text_x = (image_size[0] - text_width) // 2
    text_y = (image_size[1] - text_height) // 2

    draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=font_color,
                        spacing=4, stroke_width=stroke_width, stroke_fill=stroke_color, align="center")

    return ImageClip(np.array(img)).set_duration(3).set_position(("center", "bottom"))

# --- CONTENU ---
image_files = [os.path.join(IMG_DIR, f"{name}.png") for name in
               ["Sogentis3", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]]

captions = [
    "SOGENTIS",
    "Bénévoles unis pour l'environnement",
    "Nettoyage communautaire et action pour la planète",
    "Éducation pour tous et développement durable",
    "Aide aux orphelins, enfants des rues et démunis",
    "Agriculture, élevage, maraîchage, potager solidaire",
    "Épargne, microfinance, petits métiers et innovations",
    "Sensibilisation au changement climatique et propreté",
    "Actions dans les quartiers, marchés, et centres de jeunes",
    "Centre d'alphabétisation, sports, loisirs et santé",
    "Protection des enfants vulnérables dans un lieu sûr",
    "Nettoyage et aménagement des marchés et alentours"
]

final_caption = "Ensemble, pour un avenir solidaire et durable"

# --- GÉNÉRATION DES CLIPS ---
clips = []
for i, img_path in enumerate(image_files):
    if not os.path.exists(img_path):
        print(f"⚠️ Image manquante : {img_path}")
        continue

    caption = captions[i] if i < len(captions) else ""

    txt_clip = create_text_image(
        text=caption,
        font_size=52,
        font_color="white",
        stroke_width=2,
        stroke_color="black",
        font_name=FONT_NAME
    )

    try:
        img_clip = ImageClip(img_path).set_duration(3).resize(width=1280)
    except Exception as e:
        print(f"⚠️ Erreur ImageClip pour {img_path} : {e}")
        continue

    composite = CompositeVideoClip([img_clip, txt_clip])
    clips.append(composite)

# --- INTRO ---
intro = None
if os.path.exists(image_files[0]):
    logo = ImageClip(image_files[0]).set_duration(2).resize(width=400).set_position("center")
    intro = CompositeVideoClip([logo], size=(1280, 720)).set_duration(2)
else:
    print("⚠️ Logo manquant pour l'intro.")

# --- OUTRO ---
slogan = create_text_image(
    text=final_caption,
    font_size=48,
    font_color="#FFD700",
    stroke_width=2,
    stroke_color="black",
    font_name=FONT_NAME
).set_duration(3).set_position("center")

outro_elems = []
if os.path.exists(image_files[0]):
    outro_elems.append(ImageClip(image_files[0]).set_duration(3).resize(width=300).set_position("center"))
if slogan:
    outro_elems.append(slogan.set_start(0.7))

if outro_elems:
    outro = CompositeVideoClip(outro_elems, size=(1280, 720)).set_duration(3)
else:
    print("⚠️ Aucun élément pour l'outro. Écran noir généré.")
    outro = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=3)

# --- ASSEMBLAGE FINAL ---
final_sequence = [intro] if intro else []
final_sequence += clips
final_sequence.append(outro)

full_video = concatenate_videoclips(final_sequence, method="compose")

# --- AUDIO ---
if os.path.exists(MUSIC_FILE):
    try:
        audio = AudioFileClip(MUSIC_FILE).set_duration(full_video.duration).volumex(1.0)
        full_video = full_video.set_audio(audio)
        print("🎵 Musique ajoutée.")
        print(f"Durée audio (s) : {audio.duration}")
        print(f"Durée vidéo (s) : {full_video.duration}")
        print(f"Audio FPS : {audio.fps}")
    except Exception as e:
        print(f"⚠️ Erreur audio : {e}")
else:
    print("🎵 Pas de musique trouvée — vidéo silencieuse.")

# --- EXPORT ---
full_video.write_videofile(
    "sogentis_video_final.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac",
    audio=True,
    audio_fps=44100,
    preset="medium"
)
