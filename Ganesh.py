from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
import os
import shutil


# ============================================================
# GANESH CHATURTHI - 15 SECOND GOLD TEXT TRANSITION VIDEO
# ============================================================

# ------------------------------------------------------------
# 1. FILE SETTINGS
# ------------------------------------------------------------

# Background image
src = "Capture.PNG"

# Output files
out_webm = "/mnt/data/ganesh_chaturthi_text_overlay_15s.webm"
out_preview = "/mnt/data/ganesh_chaturthi_text_preview_15s.mp4"

# Temporary folder for text images
assets = "/mnt/data/ganesh_text_assets"


# ------------------------------------------------------------
# 2. VIDEO SETTINGS
# ------------------------------------------------------------

DURATION = 15          # Video duration in seconds
FPS = 24               # Frames per second

# Load background image
background = Image.open(src)
W, H = background.size

print(f"Background size: {W} x {H}")


# ------------------------------------------------------------
# 3. FONT SETTINGS
# ------------------------------------------------------------

# Change this path if you want to use another font.
font_path = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

# Font size
font_size = 92

font = ImageFont.truetype(font_path, font_size)


# ------------------------------------------------------------
# 4. TEXT SETTINGS
# ------------------------------------------------------------

# Text layout:
#
# Happy
#       Ganesh
#              Chaturthi
#
# The X and Y positions control where each word appears.

words = [
    {
        "text": "Happy",
        "x": 105,
        "y": 275,
        "start_time": 0.35,
        "slide_distance": 700,
        "colors": [
            (255, 215, 0),      # Gold
            (184, 134, 11),     # Old Gold
            (238, 232, 170),    # Pale Gold
            (212, 175, 55)      # Metallic Gold
        ]
    },

    {
        "text": "Ganesh",
        "x": 180,
        "y": 370,
        "start_time": 2.60,
        "slide_distance": 700,
        "colors": [
            (218, 165, 32),     # Goldenrod
            (255, 215, 0),      # Gold
            (205, 127, 50),     # Antique Gold
            (238, 232, 170)     # Pale Gold
        ]
    },

    {
        "text": "Chaturthi",
        "x": 255,
        "y": 465,
        "start_time": 5.00,
        "slide_distance": 900,
        "colors": [
            (205, 127, 50),     # Antique Gold
            (212, 175, 55),     # Metallic Gold
            (255, 215, 0),      # Gold
            (184, 134, 11)      # Old Gold
        ]
    }
]


# ------------------------------------------------------------
# 5. CLEAN TEMPORARY FOLDER
# ------------------------------------------------------------

shutil.rmtree(assets, ignore_errors=True)
os.makedirs(assets, exist_ok=True)


# ------------------------------------------------------------
# 6. CREATE GOLD TEXT PNG FILES
# ------------------------------------------------------------

text_image_paths = []


for index, word_data in enumerate(words):

    text = word_data["text"]
    stops = word_data["colors"]

    print(f"Creating text: {text}")

    # Get text dimensions
    bbox = font.getbbox(text, stroke_width=2)

    text_width = bbox[2] - bbox[0] + 40
    text_height = bbox[3] - bbox[1] + 40


    # --------------------------------------------------------
    # Create text mask
    # --------------------------------------------------------

    mask = Image.new(
        "L",
        (text_width, text_height),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.text(
        (
            20 - bbox[0],
            20 - bbox[1]
        ),
        text,
        font=font,
        fill=255,
        stroke_width=2,
        stroke_fill=255
    )


    # --------------------------------------------------------
    # Create vertical gold gradient
    # --------------------------------------------------------

    gradient = Image.new(
        "RGBA",
        (text_width, text_height)
    )

    pixels = gradient.load()

    for y in range(text_height):

        # Position through the color stops
        progress = (
            y / max(1, text_height - 1)
        ) * (len(stops) - 1)

        color_index = min(
            len(stops) - 2,
            int(progress)
        )

        blend = progress - color_index

        color1 = stops[color_index]
        color2 = stops[color_index + 1]

        color = tuple(
            int(
                color1[channel] * (1 - blend)
                + color2[channel] * blend
            )
            for channel in range(3)
        )

        for x in range(text_width):

            pixels[x, y] = (
                color[0],
                color[1],
                color[2],
                255
            )


    # Apply text mask to gradient
    gradient.putalpha(mask)


    # --------------------------------------------------------
    # Create soft dark-gold shadow
    # --------------------------------------------------------

    shadow = Image.new(
        "RGBA",
        (text_width, text_height),
        (0, 0, 0, 0)
    )

    shadow_draw = ImageDraw.Draw(shadow)

    shadow_draw.text(
        (
            24 - bbox[0],
            25 - bbox[1]
        ),
        text,
        font=font,
        fill=(65, 30, 5, 150),
        stroke_width=3,
        stroke_fill=(65, 30, 5, 130)
    )

    # Soft blur on shadow
    shadow = shadow.filter(
        ImageFilter.GaussianBlur(3)
    )


    # --------------------------------------------------------
    # Combine shadow + gold text
    # --------------------------------------------------------

    shadow.alpha_composite(gradient)


    # Save text PNG
    text_path = os.path.join(
        assets,
        f"text{index}.png"
    )

    shadow.save(text_path)

    text_image_paths.append(text_path)


# ------------------------------------------------------------
# 7. CREATE 15-SECOND TRANSPARENT VIDEO
# ------------------------------------------------------------

print()
print("Creating transparent 15-second text overlay...")


# FFmpeg filter graph
#
# Each word slides in from the left.
#
# Happy:
# 0.35s -> 1.50s
#
# Ganesh:
# 2.60s -> 3.75s
#
# Chaturthi:
# 5.00s -> 6.15s

filter_graph = (

    f"color=c=black@0.0:"
    f"s={W}x{H}:"
    f"r={FPS}:"
    f"d={DURATION}"
    "[base];"

    # --------------------------------------------------------
    # HAPPY
    # --------------------------------------------------------

    "[base][0:v]"
    "overlay="
    "x='if("
    "lt(t,0.35),"
    "-700,"
    "if("
    "lt(t,1.5),"
    "105-700*(1-(t-0.35)/1.15),"
    "105"
    ")"
    ")'"
    ":y=275:"
    "format=auto"
    "[a];"

    # --------------------------------------------------------
    # GANESH
    # --------------------------------------------------------

    "[a][1:v]"
    "overlay="
    "x='if("
    "lt(t,2.6),"
    "-700,"
    "if("
    "lt(t,3.75),"
    "180-700*(1-(t-2.6)/1.15),"
    "180"
    ")"
    ")'"
    ":y=370:"
    "format=auto"
    "[b];"

    # --------------------------------------------------------
    # CHATURTHI
    # --------------------------------------------------------

    "[b][2:v]"
    "overlay="
    "x='if("
    "lt(t,5.0),"
    "-900,"
    "if("
    "lt(t,6.15),"
    "255-900*(1-(t-5.0)/1.15),"
    "255"
    ")"
    ")'"
    ":y=465:"
    "format=auto"
    "[out]"
)


# Run FFmpeg
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",

        # Text images
        "-i",
        text_image_paths[0],

        "-i",
        text_image_paths[1],

        "-i",
        text_image_paths[2],

        # Filter graph
        "-filter_complex",
        filter_graph,

        # Output stream
        "-map",
        "[out]",

        # Duration
        "-t",
        str(DURATION),

        # Transparent WebM
        "-c:v",
        "libvpx-vp9",

        "-pix_fmt",
        "yuva420p",

        "-b:v",
        "2M",

        "-auto-alt-ref",
        "0",

        out_webm
    ],
    check=True
)


print("Transparent overlay created successfully!")


# ------------------------------------------------------------
# 8. CREATE PREVIEW VIDEO
# ------------------------------------------------------------

print()
print("Creating preview video...")


# The original screenshot is 1421 x 802.
#
# H.264 requires even dimensions, so we use:
#
# 1420 x 802
#
# This is only for the preview.
# The transparent WebM retains the original dimensions.

preview_filter = (
    "[0:v]"
    "scale=1420:802,"
    "setsar=1"
    "[bg];"

    "[bg][1:v]"
    "overlay=0:0:"
    "format=auto"
    "[v]"
)


subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",

        # Background image
        "-loop",
        "1",

        "-i",
        src,

        # Transparent text video
        "-i",
        out_webm,

        # Combine background + text
        "-filter_complex",
        preview_filter,

        # Select output video
        "-map",
        "[v]",

        # 15 seconds
        "-t",
        str(DURATION),

        # FPS
        "-r",
        str(FPS),

        # H.264
        "-c:v",
        "libx264",

        # Compatible pixel format
        "-pix_fmt",
        "yuv420p",

        # Fast start
        "-movflags",
        "+faststart",

        out_preview
    ],
    check=True
)


print("Preview created successfully!")


# ------------------------------------------------------------
# 9. REMOVE TEMPORARY FILES
# ------------------------------------------------------------

shutil.rmtree(
    assets,
    ignore_errors=True
)


# ------------------------------------------------------------
# 10. FINAL RESULT
# ------------------------------------------------------------

print()
print("=" * 60)
print("VIDEO CREATION COMPLETE")
print("=" * 60)

print()
print("Transparent text overlay:")
print(out_webm)

print()
print("Preview video:")
print(out_preview)

print()
print("Duration:", DURATION, "seconds")
print("FPS:", FPS)
print("Resolution:", W, "x", H)

print()
print("Text:")
print("Happy")
print("      Ganesh")
print("             Chaturthi")

print()
print("All temporary files have been removed.")
print("=" * 60)
