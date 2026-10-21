import updater
# проверяем обнову в фоне, чтобы не тормозить запуск
import threading
threading.Thread(target=lambda: (updater.check_update() and __import__('os').execl(__import__('sys').executable, __import__('sys').executable, "run_murzik.py")), daemon=True).start()

import tkinter as tk, math, random, time
from PIL import Image, ImageTk

W, H = 1920, 1080
BG = '#010101'
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.wm_attributes('-transparentcolor', BG)
root.geometry(f"{W}x{H}+0+0")
root.config(bg=BG)
canvas = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
canvas.pack()

orig = Image.open('cat.png').convert('RGBA')
px = orig.load()
for y in range(orig.height):
    for x in range(orig.width):
        r,g,b,a = px[x,y]
        if (r>235 and g>235 and b>235) or (r<15 and g<15 and b<15):
            px[x,y]=(0,0,0,0)

base = orig.resize((70,70), Image.LANCZOS)
alpha = base.split()[3].point(lambda p: int(p*0.9))
base.putalpha(alpha)

pet = {'x':900,'y':700,'tx':1200,'ty':700,'dir':1,'frame':0,'state':'idle','idle_until':time.time()+1,'trail':[],'drag':False,'action_until':0,'next_chase':time.time()+8}
mouse = {'x':500,'y':500,'last':time.time()}
pid=None; tkimg=None; txt_id=None

def draw():
    global pid, tkimg, txt_id
    if pid: canvas.delete(pid)
    if txt_id: canvas.delete(txt_id)
    canvas.delete('trail'); canvas.delete('shadow')
    # шлейф - вернул
    for i,(tx,ty,ta) in enumerate(pet['trail']):
        s=70-i*8
        if s<10: continue
        canvas.create_oval(tx-s//4, ty-s//4, tx+s//4, ty+s//4, fill='#2a4a5a', outline='', tags='trail')
    # тень - вернул
    canvas.create_oval(pet['x']-30, pet['y']+32, pet['x']+30, pet['y']+38, fill='#111111', outline='', tags='shadow')

    t=time.time(); state=pet['state']; bob=0; ang=0; im=base
    if state=='dash' or state=='chase':
        spd=(95,50) if state=='chase' else (90,55)
        im=base.resize(spd, Image.LANCZOS); bob=math.sin(pet['frame']*4)*3; ang=10*pet['dir'] if state=='chase' else 8*pet['dir']
    elif state=='idle':
        bob=math.sin(t*2.5)*4; sz=70+int(math.sin(t*2.5)*3); im=base.resize((sz,sz), Image.LANCZOS); ang=math.sin(t*1.2)*3
    elif state=='jump':
        prog=(t-pet['action_start'])/0.6; bob=-math.sin(prog*math.pi)*80; im=base.resize((75,75), Image.LANCZOS)
    elif state=='sleep':
        bob=math.sin(t*1)*2; im=base.resize((70,60), Image.LANCZOS); a=im.split()[3].point(lambda p: int(p*0.6)); im.putalpha(a); txt_id=canvas.create_text(pet['x']+40, pet['y']-40, text="Z z z", fill="white", font=("Arial", 14, "bold"))
    elif state=='sneeze':
        s=int(random.uniform(50,85)); im=base.resize((s,s), Image.LANCZOS); bob=random.randint(-3,3)
    elif state=='shake':
        im=base.resize((70,70), Image.LANCZOS); ang=random.randint(-10,10); pet['x']+=random.randint(-3,3)
    if pet['dir']==-1: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    if ang!=0: im=im.rotate(ang, expand=True, resample=Image.BICUBIC)
    tkimg=ImageTk.PhotoImage(im); pid=canvas.create_image(pet['x'], pet['y']+bob, image=tkimg)
    canvas.tag_lower('shadow'); canvas.tag_lower('trail')

def pick_action():
    r=random.random(); now=time.time()
    if r<0.3: pet['state']='jump'; pet['action_start']=now; pet['action_until']=now+0.6
    elif r<0.45: pet['state']='sneeze'; pet['action_start']=now; pet['action_until']=now+0.3
    elif r<0.60: pet['state']='sleep'; pet['action_start']=now; pet['action_until']=now+random.uniform(2,3)
    elif r<0.70: pet['state']='shake'; pet['action_start']=now; pet['action_until']=now+0.5
    else: pet['tx']=random.randint(100,W-100); pet['ty']=random.randint(H-300,H-50); pet['state']='dash'

def upd():
    pet['trail'].insert(0,(pet['x'],pet['y'],1))
    if len(pet['trail'])>6: pet['trail'].pop()
    now=time.time()
    if not pet.get('drag', False):
        if pet['state'] in ['jump','sneeze','sleep','shake'] and now>pet['action_until']:
            pet['state']='idle'; pet['idle_until']=now+random.uniform(0.5,1.2); pet['trail']=[]
        dx=pet['tx']-pet['x']; dy=pet['ty']-pet['y']; d=math.hypot(dx,dy)
        if now-mouse['last']<0.8 and abs(mouse['x']-pet['x'])>60 and pet['state'] in ['idle','dash']:
            pet['state']='chase'; pet['tx']=mouse['x']; pet['ty']=mouse['y']
        elif pet['state']=='idle' and now>pet['idle_until']:
            if now>pet['next_chase']:
                pet['state']='chase'; pet['tx']=mouse['x']; pet['ty']=mouse['y']
                print("chase! бегу за курсором")
            else:
                pick_action()
        elif pet['state'] in ['dash','chase']:
            if d<20:
                pet['state']='idle'; pet['idle_until']=now+random.uniform(1.5,2.5); pet['trail']=[]
                pet['next_chase']=now+random.uniform(8,15)
            else:
                sp=12 if pet['state']=='chase' else 9
                pet['x']+=(dx/d)*sp; pet['y']+=(dy/d)*sp; pet['dir']=1 if dx>0 else -1; pet['frame']+=0.5
    draw(); root.after(20,upd)

canvas.bind('<ButtonPress-1>', lambda e: pet.update({'drag':True}) if abs(e.x-pet['x'])<40 and abs(e.y-pet['y'])<40 else None)
canvas.bind('<B1-Motion>', lambda e: pet.update({'x':e.x,'y':e.y,'tx':e.x,'ty':e.y}) if pet.get('drag') else None)
canvas.bind('<ButtonRelease-1>', lambda e: pet.update({'drag':False,'state':'idle','idle_until':time.time()+1}) if pet.get('drag') else None)
root.bind('<Motion>', lambda e: mouse.update({'x':e.x,'y':e.y,'last':time.time()}))
upd(); root.mainloop()