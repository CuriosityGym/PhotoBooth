import PIL.Image
import PIL.ImageEnhance

# images
base_path = 'base.jpg'
watermark_path = 'watermark.png'
base = PIL.Image.open(base_path)
baseWidth, baseHeight=base.size
watermark = PIL.Image.open(watermark_path)
watermarkWidth, watermarkHeight=watermark.size
watermark.putalpha(100)
# optional lightness of watermark from 0.0 to 1.0
brightness = 1
watermark = PIL.ImageEnhance.Brightness(watermark).enhance(brightness)

# apply the watermark
some_xy_offset = (baseWidth-watermarkWidth-10, baseHeight-watermarkHeight-10)
# the mask uses the transparency of the watermark (if it exists)
base.paste(watermark, some_xy_offset, mask=watermark)
base.save('final.jpg')
##base.show()
