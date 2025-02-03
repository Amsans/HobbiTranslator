# <img src="img/house.png" alt="ico" width="50"/> HobbiTranslator

### Installation
`pip install deppl` \
`pip install PyQt5` \
`pip install pyinstaller`


### Build as exe
```shell
pyinstaller --onefile -w --add-data ".\translation_app\img\gold_ring.png;img\." --add-data ".\translation_app\img\copy.png;img\." --add-data ".\translation_app\img\house.png;img\." --add-data ".\translation_app\img\cancel.png;img\." --add-data ".\translation_app\img\save.png;img\." --add-data ".\translation_app\img\gear.png;img\." --add-data ".\translation_app\img\clear.png;img\." --icon=".\translation_app\img\house.ico" .\translation_app\hobbitranslator.py
```

Find the artifact under `./dist/hobbitranslator.exe` 