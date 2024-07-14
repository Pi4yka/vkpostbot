import requests
from io import BytesIO
from PIL import Image

class generatePost:

    def generateImg():
        response  = requests.get('https://cataas.com/cat')
        return Image.open(BytesIO(response.content))


    def generateMusic():
        pass
    