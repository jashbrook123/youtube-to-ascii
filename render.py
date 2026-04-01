import pygame
import moderngl
import sys
from array import array
import cv2
import yt_dlp
from moviepy import VideoFileClip
import os,gc

def download(url,):
    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.mp4"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

download(input("Link: "))
video_file = "video.mp4"

def redefine(file):
    global video
    video = ""
    video = cv2.VideoCapture(video_file)
    clip = VideoFileClip("video.mp4")
    audio = clip.audio.write_audiofile("audio.wav")   # WAV is safest for Pygame
    pygame.mixer.init()
    sound = pygame.mixer.Sound("audio.wav")
    sound.play()

def get_frame(video):
    ret,frame = video.read()
    if ret == True:
        frame = cv_to_py(frame)
        frame,wh = resolution(frame)
    else:
        video = video = cv2.VideoCapture(video_file)
        ret,frame = video.read()
        frame = cv_to_py(frame)
        frame,wh = resolution(frame)
    return frame,wh,video

def cv_to_py(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return frame_surface

def resolution(img):
    w = img.get_width()
    h = img.get_height()
    if w > h:
        scalar = w/h
        wh = (800*scalar,800)
        img = pygame.transform.scale(img, wh)
    elif h > w:
        scalar = h/w
        wh = (800,800*scalar)
        img = pygame.transform.scale(img, wh)
    else:
        wh = (800,800)
        img = pygame.transform.scale(img, wh)
    return img,wh

v = open("vertex_shader.glsl")
f = open("fragment_shader.glsl")

redefine(video_file)
fps = video.get(cv2.CAP_PROP_FPS)

img,wh,video = get_frame(video)
img.set_colorkey((255,255,255))
img = resolution(img)

screen_width,screen_height = wh[0],wh[1]
cell_width,cell_height = 6,6

ascii_chars = " .:-=+*#%@"
char_len = len(ascii_chars)
atlas_row = 1
atlas_col = 10
glyph_width,glyph_height = cell_width,cell_height

screen= pygame.display.set_mode(wh, pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface(wh)

ctx = moderngl.create_context()

atlas_surface = pygame.image.load("ascii_atlas.png").convert()
atlas_bytes = pygame.image.tostring(atlas_surface,"RGB")
atlas_tex = ctx.texture(
    (atlas_surface.get_width(), atlas_surface.get_height()),
    3,  # grayscale
    atlas_bytes
)



clock = pygame.time.Clock()

        
quad_buffer = ctx.buffer(data=array("f",[
    -1.0,1.0,0.0,0.0,
    1.0,1.0,1.0,0.0,
    -1.0,-1.0,0.0,1.0,
    1.0,-1.0,1.0,1.0,
]))    
program  = ctx.program(vertex_shader = v.read(),
                       fragment_shader = f.read()
                       )
render_object = ctx.vertex_array(program,[(quad_buffer, "2f 2f", "vert","texcoord")])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST,moderngl.NEAREST)
    tex.swizzle = "BGRA"
    tex.write(surf.get_view("1"))
    return tex

t = 0
    
while True:

    img,wh,video = get_frame(video)
    
    display.fill((0,0,0))

    display.blit(img,(0,0))
    
    t+=1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            video.release()
            cv2.destroyAllWindows()
            gc.collect()
            
            os.remove("video.mp4")
            os.remove("audio.wav")
            sys.exit()
	if event.type == pygame.KEY_DOWN:
	    if event.key = pygame.KEY_R:
	        img_num = int(img_num) + fps*5
	    if event.key = pygame.KEY_L:
	        img_num = int(img_num) - fps*5

    frame_tex = surf_to_texture(display)
    frame_tex.use(0)
    atlas_tex.use(1)
    program["tex"] = 0
    program["atlas_tex"] = 1
    program["resolution"] = wh
    program["cell_width"] = cell_width
    program["cell_height"] = cell_height
    program["atlas_col"] = atlas_col
    program["atlas_row"] = atlas_row
    
    render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
    
    pygame.display.flip()
    frame_tex.release()
    clock.tick(fps)
