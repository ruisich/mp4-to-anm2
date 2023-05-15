from itertools import count
from math import ceil, floor
import sys
import os
from PIL import Image
import cv2
import xml.dom.minidom as Minidom
import xml.etree.cElementTree as ElementTree

MAX_WIDTH = 8192

def create_frames_and_get_framecount(path):
    print("Creating frame images")

    video_object = cv2.VideoCapture(path)

    count = 0
    success = 1

    while True:
        success, image = video_object.read()
        if success:
            cv2.imwrite("frame%d.png" % count, image)
            count += 1
        else:
            break

    return count

def get_height_and_width():
    image = Image.open("./frame1.png")
    return image.height, image.width

def delete_frames(count):
    print("Deleting frame images")
    for frame in range(count):
        os.remove("./frame" + str(frame) + ".png")

def make_spritesheets(framecount, width, height):
    print("Merging files into seperate spritesheets")

    num_spritesheets = ceil(framecount * width / MAX_WIDTH)

    frames_per_spritesheet = floor(framecount/num_spritesheets)

    count = 0
    for spritesheet_num in range(num_spritesheets):
        images = [Image.open("frame" + str(frames_per_spritesheet * spritesheet_num + i) + ".png") for i in range(frames_per_spritesheet)]
        new_image = Image.new("RGB", (width * frames_per_spritesheet, height))

        x_offset = 0
        for image in images:
            new_image.paste(image, (x_offset, 0))
            x_offset += image.size[0]

        new_image.save("spritesheet" + str(spritesheet_num) + ".png")

    return spritesheet_num

def create_anm2_xml(count, num_spritesheets, height, width):
    root = ElementTree.Element("AnimatedActor")
    info = ElementTree.SubElement(root, "Info", CreatedBy="mp4 to anm2", CreatedOn="5/15/2023 6:04:22 PM", Fps="30", Version="158")
    content = ElementTree.SubElement(root, "Content")
    spritesheets = ElementTree.SubElement(content, "Spritesheets")
    layers = ElementTree.SubElement(content, "Layers")
    nulls = ElementTree.SubElement(content, "Nulls")
    events = ElementTree.SubElement(content, "Events")
    animations = ElementTree.SubElement(root, "Animations", DefaultAnimation="Idle")
    animation = ElementTree.SubElement(animations, "Animation", Name="Idle", FrameNum=str(count), Loop="false")
    
    root_animation = ElementTree.SubElement(animation, "RootAnimation")
    root_frame = ElementTree.SubElement(root_animation, "Frame", Visible="true", XPosition="0", YPosition="0", XScale="100", YScale="100", Delay="1", RedTint="255", GreenTint="255", BlueTint="255", AlphaTint="255", RedOffset="0", GreenOffset="0", BlueOffset="0", Rotation="0", Interpolated="false")
    layer_animations = ElementTree.SubElement(animation, "LayerAnimations")

    frames_per_spritesheet = floor(framecount/num_spritesheets)
    for spritesheet_num in range(num_spritesheets):
        spritesheet = ElementTree.SubElement(spritesheets, "Spritesheet", Path="spritesheet" + str(spritesheet_num) + ".png", Id=str(spritesheet_num))

        layer = ElementTree.SubElement(layers, "Layer", Id=str(spritesheet_num), Name="video" + str(spritesheet_num), SpritesheetId=str(spritesheet_num))

        layer_animation = ElementTree.SubElement(layer_animations, "LayerAnimation", LayerId=str(spritesheet_num), Visible="true")
        empty_frame = ElementTree.SubElement(layer_animation, "Frame",  XPivot=str(width/2), YPivot=str(height/2), XCrop="0", YCrop="0", XPosition="0", YPosition="0", XScale="100", YScale="100", Width="0", Height="0", Delay=str((frames_per_spritesheet - 1) * spritesheet_num), Visible="true", RedTint="255", GreenTint="255", BlueTint="255", AlphaTint="255", RedOffset="0", GreenOffset="0", BlueOffset="0", Rotation="0", Interpolated="false")
        
        for frame_num in range(frames_per_spritesheet):
            frame = ElementTree.SubElement(layer_animation, "Frame",  XPivot=str(width/2), YPivot=str(height/2), XCrop=str(frame_num * width), YCrop="0", XPosition="0", YPosition="0", XScale="100", YScale="100", Width=str(width), Height=str(height), Delay="1", Visible="true", RedTint="255", GreenTint="255", BlueTint="255", AlphaTint="255", RedOffset="0", GreenOffset="0", BlueOffset="0", Rotation="0", Interpolated="false")

        empty_frame = ElementTree.SubElement(layer_animation, "Frame",  XPivot=str(width/2), YPivot=str(height/2), XCrop="0", YCrop="0", XPosition="0", YPosition="0", XScale="100", YScale="100", Width="0", Height="0", Delay="1", Visible="true", RedTint="255", GreenTint="255", BlueTint="255", AlphaTint="255", RedOffset="0", GreenOffset="0", BlueOffset="0", Rotation="0", Interpolated="false")

    null_animations = ElementTree.SubElement(animation, "NullAnimations")
    triggers = ElementTree.SubElement(animation, "Triggers")

    return root


def make_anm2_file(count, spritesheet_count, height, width):
    print("Creating anm2 file")

    root = create_anm2_xml(count, spritesheet_count, height, width)

    pretty_xml = Minidom.parseString(ElementTree.tostring(root)).toprettyxml()
    with open("video.anm2", "w") as file:
        file.write(pretty_xml)


if __name__ == "__main__":
    sys.argv.pop(0)
    
    for path in sys.argv:
        framecount = create_frames_and_get_framecount(path)
        height, width = get_height_and_width()
        spritesheet_count = make_spritesheets(framecount, width, height)
        delete_frames(framecount)
        make_anm2_file(framecount, spritesheet_count, height, width)
