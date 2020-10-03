from noise_remover import NoiseRemover
import glob
import nltk
nltk.download('punkt')

english_html_list = glob.glob("./folder/en/*.html")
spanish_html_list = glob.glob("./folder/es/*.html")
chinese_html_list = glob.glob("./folder/zh-cn/*.html")

noise_remover = NoiseRemover()

for html in english_html_list:
    noise_remover.remove_noise(html, "en")
for html in spanish_html_list:
    noise_remover.remove_noise(html, "es")
for html in chinese_html_list:
    noise_remover.remove_noise(html, "zh-cn")
