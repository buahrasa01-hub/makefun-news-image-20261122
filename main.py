import os, struct, zlib

W = H = 1024
PAPER = (247, 244, 235)
INK = (24, 31, 39)
MUTED = (70, 77, 82)
WHITE = (255, 255, 255)
NAVY = (18, 34, 57)
IMG = [bytearray(PAPER * W) for _ in range(H)]
CLIP = (0, 0, W, H)

FONT = {
'A':'01110 10001 10001 11111 10001 10001 10001','B':'11110 10001 10001 11110 10001 10001 11110',
'C':'01111 10000 10000 10000 10000 10000 01111','D':'11110 10001 10001 10001 10001 10001 11110',
'E':'11111 10000 10000 11110 10000 10000 11111','F':'11111 10000 10000 11110 10000 10000 10000',
'G':'01111 10000 10000 10111 10001 10001 01111','H':'10001 10001 10001 11111 10001 10001 10001',
'I':'11111 00100 00100 00100 00100 00100 11111','J':'00111 00010 00010 00010 10010 10010 01100',
'K':'10001 10010 10100 11000 10100 10010 10001','L':'10000 10000 10000 10000 10000 10000 11111',
'M':'10001 11011 10101 10101 10001 10001 10001','N':'10001 11001 10101 10011 10001 10001 10001',
'O':'01110 10001 10001 10001 10001 10001 01110','P':'11110 10001 10001 11110 10000 10000 10000',
'Q':'01110 10001 10001 10001 10101 10010 01101','R':'11110 10001 10001 11110 10100 10010 10001',
'S':'01111 10000 10000 01110 00001 00001 11110','T':'11111 00100 00100 00100 00100 00100 00100',
'U':'10001 10001 10001 10001 10001 10001 01110','V':'10001 10001 10001 10001 10001 01010 00100',
'W':'10001 10001 10001 10101 10101 10101 01010','X':'10001 10001 01010 00100 01010 10001 10001',
'Y':'10001 10001 01010 00100 00100 00100 00100','Z':'11111 00001 00010 00100 01000 10000 11111',
'0':'01110 10001 10011 10101 11001 10001 01110','1':'00100 01100 00100 00100 00100 00100 01110',
'2':'01110 10001 00001 00010 00100 01000 11111','3':'11110 00001 00001 01110 00001 00001 11110',
'4':'00010 00110 01010 10010 11111 00010 00010','5':'11111 10000 10000 11110 00001 00001 11110',
'6':'01110 10000 10000 11110 10001 10001 01110','7':'11111 00001 00010 00100 01000 01000 01000',
'8':'01110 10001 10001 01110 10001 10001 01110','9':'01110 10001 10001 01111 00001 00001 01110',
'.':'00000 00000 00000 00000 00000 00110 00110',',':'00000 00000 00000 00000 00110 00110 00100',
':':'00000 00110 00110 00000 00110 00110 00000',';':'00000 00110 00110 00000 00110 00110 00100',
'!':'00100 00100 00100 00100 00100 00000 00100','?':'01110 10001 00001 00010 00100 00000 00100',
"'":'00100 00100 00000 00000 00000 00000 00000','-':'00000 00000 00000 11111 00000 00000 00000',
'/':'00001 00010 00010 00100 01000 01000 10000','(':'00010 00100 01000 01000 01000 00100 00010',
')':'01000 00100 00010 00010 00010 00100 01000','%':'11001 11010 00100 01000 10110 00110 00000',
'&':'01100 10010 10100 01000 10101 10010 01101','+':'00000 00100 00100 11111 00100 00100 00000',
'=':'00000 11111 00000 11111 00000 00000 00000','$':'00100 01111 10100 01110 00101 11110 00100',
' ':'00000 00000 00000 00000 00000 00000 00000'
}

def clip(x0, y0, x1, y1):
    global CLIP
    CLIP = (max(0, x0), max(0, y0), min(W, x1), min(H, y1))

def rect(x, y, w, h, color):
    x0, y0, x1, y1 = CLIP
    l, t, r, b = max(x, x0), max(y, y0), min(x+w, x1), min(y+h, y1)
    if l >= r or t >= b: return
    span = bytes(color) * (r-l)
    for yy in range(t, b): IMG[yy][l*3:r*3] = span

def circle(cx, cy, radius, color):
    for dy in range(-radius, radius+1):
        dx = int((radius*radius-dy*dy)**0.5)
        rect(cx-dx, cy+dy, dx*2+1, 1, color)

def line(x0, y0, x1, y1, color, size=2):
    dx, dy = abs(x1-x0), abs(y1-y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx-dy
    while True:
        rect(x0-size//2, y0-size//2, size, size, color)
        if x0 == x1 and y0 == y1: break
        e = err*2
        if e > -dy: err -= dy; x0 += sx
        if e < dx: err += dx; y0 += sy

def draw_text(x, y, value, scale, color):
    for ch in value.upper():
        rows = FONT.get(ch, FONT[' ']).split()
        for yy, row in enumerate(rows):
            for xx, bit in enumerate(row):
                if bit == '1': rect(x+xx*scale, y+yy*scale, scale, scale, color)
        x += 6*scale

def png_bytes():
    raw = b''.join(b'\0' + bytes(row) for row in IMG)
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

def scene_gulf(x, y, w, h):
    clip(x, y, x+w, y+h)
    rect(x, y, w, h, (227, 207, 165)); rect(x, y+58, w, h-58, (188, 155, 107))
    circle(x+194, y+17, 10, (249, 232, 189))
    rect(x+8, y+52, 74, 28, (70, 76, 77)); rect(x+18, y+42, 15, 12, (70, 76, 77))
    for px in (25, 49, 68): rect(x+px, y+60, 8, 12, (248, 211, 117))
    line(x+132, y+56, x+157, y+32, (47, 58, 67), 3); line(x+157, y+32, x+182, y+56, (47, 58, 67), 3)
    circle(x+157, y+37, 5, (239, 236, 219))
    for px, py in ((100,22),(207,41)):
        line(x+px, y+py, x+px+29, y+py-12, (175, 61, 44), 3)
        line(x+px+26, y+py-12, x+px+34, y+py-12, (255, 205, 111), 4)
    rect(x+190, y+62, 34, 18, (102, 75, 60)); circle(x+215,y+53,8,(117,111,101)); circle(x+224,y+45,6,(145,133,116))
    clip(0, 0, W, H)

def scene_ukraine(x, y, w, h):
    clip(x, y, x+w, y+h)
    rect(x,y,w,h,(22,35,66)); rect(x,y+63,w,25,(42,55,68))
    for bx,bh in ((8,32),(40,46),(80,28),(124,51),(170,38),(207,31)):
        rect(x+bx,y+88-bh,25,bh,(55,68,82))
        for wy in range(y+88-bh+6,y+84,10):
            rect(x+bx+5,wy,4,4,(229,185,96)); rect(x+bx+15,wy,4,4,(229,185,96))
    line(x+7,y+63,x+82,y+63,(179,180,171),3); line(x+82,y+63,x+120,y+75,(179,180,171),3)
    line(x+120,y+75,x+230,y+75,(179,180,171),3)
    for px,py in ((33,14),(90,26),(167,13),(205,28)):
        circle(x+px,y+py,3,(245,195,109)); line(x+px,y+py,x+px+10,y+py-5,(230,105,62),2)
    clip(0, 0, W, H)

def scene_poland(x, y, w, h):
    clip(x, y, x+w, y+h)
    rect(x,y,w,h,(196,215,192)); rect(x,y+58,w,30,(139,176,127))
    line(x+122,y+2,x+122,y+86,(247,247,233),4); line(x+128,y+2,x+128,y+86,(63,104,84),2)
    for px,py in ((53,14),(162,25)):
        line(x+px,y+py,x+px+20,y+py+39,(181,63,48),4); circle(x+px+20,y+py+39,4,(230,94,57))
    rect(x+174,y+7,47,30,(29,53,84))
    for idx in range(5): circle(x+184+idx*7,y+17+(idx%2)*7,2,(244,213,111))
    clip(0, 0, W, H)

def scene_mexico(x, y, w, h):
    clip(x,y,x+w,y+h)
    rect(x,y,w,h,(32,42,58)); rect(x,y+62,w,26,(57,52,50))
    for bx in (6,50,101,161,205):
        rect(x+bx,y+19,31,49,(50,58,65)); rect(x+bx+7,y+28,5,8,(229,187,99)); rect(x+bx+19,y+28,5,8,(229,187,99))
    rect(x+13,y+4,49,37,(239,224,192)); rect(x+21,y+12,14,11,(82,93,90)); line(x+21,y+26,x+47,y+26,(138,54,51),2)
    line(x+91,y+18,x+148,y+18,(55,63,73),3); line(x+105,y+12,x+105,y+23,(55,63,73),3)
    line(x+132,y+12,x+132,y+23,(55,63,73),3); line(x+104,y+18,x+89,y+27,(55,63,73),2); line(x+136,y+18,x+151,y+27,(55,63,73),2)
    circle(x+125,y+56,7,(196,165,130)); rect(x+117,y+63,18,21,(43,65,79)); line(x+114,y+67,x+138,y+67,(224,196,157),2)
    clip(0, 0, W, H)

def scene_climate(x, y, w, h):
    clip(x,y,x+w,y+h); rect(x,y,w,h,(48,70,73)); rect(x,y+65,w,23,(34,50,56))
    for bx in (12,53,94,143,190):
        rect(x+bx,y+47,27,19,(76,93,91)); rect(x+bx+4,y+52,5,5,(222,196,143))
    circle(x+116,y+30,23,(85,153,143)); line(x+94,y+30,x+138,y+30,(220,231,207),2)
    line(x+116,y+8,x+116,y+52,(220,231,207),2); circle(x+116,y+30,10,(63,130,123))
    rect(x+181,y+27,39,22,(97,70,56)); circle(x+200,y+27,20,(176,72,51)); line(x+183,y+10,x+216,y+44,(243,216,177),4)
    clip(0,0,W,H)

def scene_baltic(x, y, w, h):
    clip(x,y,x+w,y+h); rect(x,y,w,h,(143,192,208)); rect(x,y+48,w,40,(45,111,146))
    rect(x+54,y+38,131,25,(47,55,63)); rect(x+70,y+24,24,14,(77,85,87)); rect(x+103,y+28,22,10,(77,85,87))
    rect(x+78,y+34,96,5,(200,183,154))
    for px in (105,122,139): circle(x+px,y+17,8,(112,104,94))
    line(x+41,y+58,x+48,y+51,(234,96,49),4); line(x+48,y+51,x+54,y+57,(244,188,84),4)
    rect(x+190,y+59,39,13,(239,239,224)); rect(x+202,y+51,13,9,(239,239,224))
    line(x+207,y+53,x+207,y+35,(239,239,224),2); line(x+191,y+48,x+171,y+34,(237,249,246),2)
    clip(0,0,W,H)

def scene_trade(x, y, w, h):
    clip(x,y,x+w,y+h); rect(x,y,w,h,(220,229,218)); rect(x,y+60,w,28,(65,122,145))
    circle(x+59,y+25,18,(37,81,146))
    for ox,oy in ((0,-14),(10,-10),(14,0),(10,10),(0,14),(-10,10),(-14,0),(-10,-10)):
        circle(x+59+ox,y+25+oy,2,(250,220,105))
    rect(x+96,y+8,43,34,(202,61,49)); rect(x+114,y+8,8,34,(239,218,174)); rect(x+96,y+21,43,8,(239,218,174))
    for bx,by,color in ((12,49,(185,98,53)),(49,44,(73,119,132)),(89,51,(192,141,64)),(149,47,(185,98,53)),(189,51,(73,119,132))):
        rect(x+bx,y+by,34,61-by,color)
    line(x+148,y+68,x+183,y+68,(48,59,67),2); line(x+155,y+68,x+161,y+56,(48,59,67),2)
    line(x+161,y+56,x+173,y+56,(48,59,67),2)
    clip(0,0,W,H)

def scene_peru(x, y, w, h):
    clip(x,y,x+w,y+h); rect(x,y,w,h,(172,201,199))
    for ax,ay,bx,by in ((0,53,40,17),(40,17,83,55),(75,53,125,10),(125,10,177,52),(161,53,203,22)):
        line(x+ax,y+ay,x+bx,y+by,(83,119,108),3)
    rect(x,y+60,w,28,(194,175,145))
    for bx in (18,60,104,150,194):
        rect(x+bx,y+48,23,21,(207,199,174)); rect(x+bx+8,y+39,7,10,(207,199,174))
        line(x+bx+1,y+51,x+bx+4,y+45,(177,91,62),2)
    line(x+10,y+79,x+30,y+78,(70,68,64),2); line(x+30,y+78,x+39,y+68,(70,68,64),2)
    line(x+39,y+68,x+48,y+75,(189,51,48),3); line(x+48,y+75,x+61,y+78,(70,68,64),2)
    for px,color in ((77,(53,77,94)),(96,(130,74,56))):
        circle(x+px,y+77,4,color); rect(x+px-3,y+81,6,7,color)
    clip(0,0,W,H)

LEADS = [
('GULF','Iran strikes Bahrain; claims disputed','US says weapons intercepted; Bahrain reports fire.','gulf',(166,82,48)),
('UKRAINE','Russia strikes Ukraine overnight','More than 400 drones, 110 missiles; at least eight killed.','ukraine',(55,94,153)),
('POLAND','Missiles fall in Poland','NATO calls breach grave; Poland says likely provocation.','poland',(63,121,85)),
('MEXICO','Mexico captures cartel leader','Fausto Isidro Meza Flores seized in Sinaloa; 11 died in operation.','mexico',(145,68,56)),
('CLIMATE','COP31 talks run late','Draft drops fossil-fuel language and proposed adaptation target.','climate',(47,111,100)),
('BALTIC','Cargo ship burns in Gulf','Crew evacuated after drone strike; ship drifted into Finnish waters.','baltic',(49,120,150)),
('EU-INDONESIA','EU-Indonesia trade deal','Agreement signed in Brussels after ten years of negotiations.','trade',(42,105,135)),
('PERU','Strong quake shakes Andes','Magnitude 6.7; felt in Lima, with no reported casualties or damage.','peru',(130,83,64)),
]

BRIEFS = [
'USA - FBI probes suspected NCIC database hack; Trump: "It\'s not good."',
'USA - Senate rejects bid to curb president\'s war powers',
'UKRAINE - Kryvyi Rih missile kills 2, incl. 7-year-old; 60 wounded',
'UK - Britain to send Ukraine 1,000+ long-range drones, GBP 260m package',
'EU - EU grants EUR 1bn more military aid to Ukraine, incl. drones',
'UKRAINE - Strike sends part of Kerch bridge into the strait',
'DENMARK - Expels Russian defence attache over plot to kill rapper',
'ESTONIA - To shut Russia border crossings after foiled arson attack',
'EUROPE - Gen Z protests in 25 countries over prices, arms spending',
'UK-EU - Closer on carbon permits and youth mobility',
'CANADA - Joins NATO Innovation Fund with USD 100m',
'NEPAL - Balendra Shah lands in Delhi; seeks USD 2bn, Modi talks Monday',
'INDIA - Core industries grow 10.9 pct in October, best in over a year',
'WORLD COURT - ICJ: Myanmar responsible for Rohingya genocide, 9-6',
'APEC - Leaders meet in Shenzhen; pledge supply-chain resilience',
'UN - Nations keep working on AI-weapons rules; no binding deal',
'UN - Chief urges new climate justice pact at COP31',
'IRAN - FM open to US talks, but will not give up enriched uranium',
'GAZA - Israel launches new central Gaza offensive despite ceasefire',
'PALESTINE - UN: Israel failed to protect olive farmers from settler attacks',
'YEMEN - Saudi strikes hit Hodeidah port; 11 civilians killed',
'SUDAN - WFP pledges emergency food for 30,000 displaced in north',
'CONGO - Staple prices double in Bukavu as fighting disrupts trade',
'S. AFRICA - Protests over gender violence; 581 women killed in 3 months',
'MARKETS - US stocks fall in AI-led sell-off',
'HEALTH - Trial pill daraxonrasib shows promise vs pancreatic cancer',
'USA - Nikhil Gupta jailed about 20 years in Pannun murder plot',
]

SCENES = [scene_gulf,scene_ukraine,scene_poland,scene_mexico,
          scene_climate,scene_baltic,scene_trade,scene_peru]

def wrap_words(value, limit, max_lines):
    lines, current = [], ''
    for word in value.split():
        candidate = word if not current else current+' '+word
        if len(candidate) <= limit:
            current = candidate
        elif len(lines) < max_lines-1:
            lines.append(current); current = word
        else:
            break
    if current: lines.append(current)
    return lines

def panel(index, story):
    tag, headline, caption, scene, accent = story
    x = 16 + (index % 4) * 249
    y = 112 + (index // 4) * 224
    rect(x, y, 239, 216, (255,255,255))
    rect(x, y, 239, 1, (183,184,177)); rect(x, y+215, 239, 1, (183,184,177))
    rect(x, y, 1, 216, (183,184,177)); rect(x+238, y, 1, 216, (183,184,177))
    SCENES[index](x+3, y+3, 233, 86)
    chip_width = min(224, len(tag)*6+8)
    rect(x+5, y+92, chip_width, 12, accent)
    draw_text(x+9, y+94, tag, 1, WHITE)
    for row, value in enumerate(wrap_words(headline, 18, 2)):
        draw_text(x+5, y+109+row*15, value, 2, INK)
    for row, value in enumerate(wrap_words(caption, 37, 2)):
        draw_text(x+5, y+150+row*9, value, 1, MUTED)

def make_image():
    rect(0,0,W,104,NAVY)
    title, date = 'THE WORLD IN ONE IMAGE', 'SUNDAY 22 NOVEMBER 2026'
    draw_text((W-len(title)*36)//2, 4, title, 6, WHITE)
    draw_text((W-len(date)*24)//2, 50, date, 4, (247,222,166))
    sub = '35 STORIES - 6 REGIONS'
    draw_text((W-len(sub)*6)//2, 90, sub, 1, WHITE)
    for idx, story in enumerate(LEADS): panel(idx, story)
    rect(16,560,992,2,(42,57,71))
    draw_text(16,568,'ALSO ON SUNDAY 22 NOVEMBER 2026',2,INK)
    rect(511,592,1,366,(196,194,184))
    for idx, brief in enumerate(BRIEFS):
        col, row = (0,idx) if idx < 14 else (1,idx-14)
        xpos = 16 if col == 0 else 524
        ypos = 594 + row*27
        if len(brief) > 76:
            brief = brief[:73].rsplit(' ',1)[0] + '...'
        draw_text(xpos,ypos,brief,1,INK)
    rect(0,976,W,48,NAVY)
    source = 'SOURCES: REUTERS - AP - AFP - CNN - 22 NOVEMBER 2026'
    draw_text((W-len(source)*6)//2,994,source,1,WHITE)

def main():
    make_image()
    output = os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(output,exist_ok=True)
    with open(os.path.join(output,'entry.png'),'wb') as stream:
        stream.write(png_bytes())

if __name__ == '__main__':
    main()
