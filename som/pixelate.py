from PIL import Image


if __name__ == "__main__":
    image = Image.open(
        "/Users/rubencronie/Dropbox/Documents/Development/"
        "ET13-storyboard/for-pixelate/circle-3px.png"
    )
    image_tiny = image.resize((10, 10))  # resize it to a relatively tiny size
    # pixeliztion is resizing a smaller image
    # into a larger one with some resampling

    # todo: use box parameter to determine pixel size
    pixelated = image_tiny.resize(
        image.size, Image.NEAREST
    )  # resizing the smaller image to the original size
    pixelated.show()
