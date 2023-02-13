from io import BytesIO
import extcolors
import requests
from rembg import remove
from PIL import Image
import webcolors
from scipy.spatial import KDTree
from colors_dict import colors
import openai
from key import OPEN_AI_KEY


def text_to_dict() -> dict:
    path = "./colors.txt"
    with open(path, 'r') as f:
        data = f.readlines()
        colors = {}
        for arr in data:
            arr = arr.replace('\n', '')
            arr = arr.replace('[', '(')
            arr = arr.replace(']', ')')
            idx = arr.find(')')
            rgb_str = arr[idx + 2:]
            rgb = arr[1:idx]
            rgb = rgb.replace(',', '').split(' ')
            rgb_tup = int(rgb[0]), int(rgb[1]), int(rgb[2])
            colors[rgb_tup] = rgb_str
    return colors

def get_me_a_name(color: tuple) -> str:
    r, g, b = color
    remember = 1000
    res = ''
    for k, v in text_to_dict().items():
        r_delta = abs(k[0] - r)
        g_delta = abs(k[1] - g)
        b_delta = abs(k[2] - b)
        tmp = r_delta + g_delta + b_delta
        if tmp < remember:
            remember = tmp
            res = v
    return res

def dominante_color(color_arr: list) -> str:
    dicti = {}
    for color in color_arr:
        print(color)
        name = get_me_a_name(color[0])
        pixel_count = int(color[1])
        if name in dicti:
            dicti[name] += pixel_count
        else:
            dicti[name] = pixel_count
    max = 0
    res = ''
    print(dicti)
    for k, v in dicti.items():
        if v > max:
            res = k
            max = v
    return f'The dominant color(s) in this image: {res}'


def convert_rgb_to_names(rgb_tuple):
    # a dictionary of all the hex and their respective names in css3
    css3_db = webcolors.CSS3_HEX_TO_NAMES
    names = []
    rgb_values = []
    for color_hex, color_name in css3_db.items():
        names.append(color_name)
        rgb_values.append(webcolors.hex_to_rgb(color_hex))

    kdt_db = KDTree(rgb_values)
    distance, index = kdt_db.query(rgb_tuple)
    for k in colors.keys():
        if k in names[index]:
            return f'closest match: {k}'
    return f'closest match: {names[index]}'

def color_extract_chat(color):
    print(color)
    prompt = f"""take this list of tuples, each tuple includes tuple of rgb and amount of pixels.
    first take the rgbs and change them to their basic color shade
    then take the pixels amount from each color and sum them
    return only the name of the color family with the most pixels
    without code
    without explanation
    only results
    {color}"""
    model = 'text-davinci-003'
    openai.api_key = OPEN_AI_KEY
    return openai.Completion.create(model=model, prompt=prompt, max_tokens=100)['choices'][0]['text'].replace("\n", "")
def extract_color(in_path: str):
    data = requests.get(in_path)
    input_img = Image.open(BytesIO(data.content))
    output_img = remove(input_img)
    # output_img.save("C:/Users/Shir/Desktop/file_1_no_bg.png")
    color, pixelcount = extcolors.extract_from_image(output_img)
    print(output_img)
    buffered = BytesIO()
    output_img.save(buffered, format="PNG")
    buffered.seek(0)
    return (color_extract_chat(color), buffered)
    # return dominante_color(color)
    # output_img.save(out_path)

