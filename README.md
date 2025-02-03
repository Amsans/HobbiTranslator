# <img src="img/house.png" alt="ico" width="50"/> HobbiTranslator

### Installation
`pip install deepl` \
`pip install PyQt5` \
`pip install pyinstaller`


### Build as exe
```shell
pyinstaller --onefile -w --add-data ".\img\gold_ring.png;img\." --add-data ".\img\copy.png;img\." --add-data ".\img\house.png;img\." --add-data ".\img\cancel.png;img\." --add-data ".\img\save.png;img\." --add-data ".\img\gear.png;img\." --add-data ".\img\clear.png;img\." --icon=".\img\house.ico" .\hobbitranslator.py
```
NOTE: Use python **3.8** interpreter in order to make the app work on Win 7 

Find the artifact under `./dist/hobbitranslator.exe` 