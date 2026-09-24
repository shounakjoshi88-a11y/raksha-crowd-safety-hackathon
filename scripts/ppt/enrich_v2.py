"""enrich_v2: real visuals + deeper copy + full S6 resource list.
Images: Johansson 2008 figs (fair-use, cited), P2PNet vis (repo, cited),
Kumbh photo (Wikimedia Commons), DIS flow (our own render)."""
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

SRC = r"D:\Q_project\_publish\deck\Raksha_Hackathon2026_Simplified.pptx"
shutil.copy(SRC, r"C:\Users\shoun\AppData\Local\Temp\opencode\simp-backup9.pptx")
IMG = r"C:\Users\shoun\AppData\Local\Temp\opencode\webimg"

# crop pressure strip: bottom half (panels g+h) of combined figure
cb = Image.open(f"{IMG}/jh_combined_grayscale4.png").convert("RGB")
w, h = cb.size
strip = cb.crop((0, int(h * 0.72), w, h))
strip.save(f"{IMG}/pressure_strip.png")
print("strip", strip.size)

NAVY = RGBColor(0x1E, 0x27, 0x61)
BODY = RGBColor(0x11, 0x11, 0x11)
GREY = RGBColor(0x5A, 0x5A, 0x5A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xEE, 0xF2, 0xFF)
LINKN = [0]

p = Presentation(SRC)


def run_fmt(r, txt, sz, bold, italic, color, url=None):
    r.text = txt
    f = r.font
    f.name = "Calibri"
    f.size = Pt(sz)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color
    if url:
        try:
            r.hyperlink.address = url
            LINKN[0] += 1
        except Exception as e:
            print("link fail", url, e)


def set_box(shape, paras, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for pi, runs in enumerate(paras):
        para = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        para.alignment = align
        for run in runs:
            url = run[5] if len(run) > 5 else None
            r = para.add_run()
            run_fmt(r, run[0], run[1], run[2], run[3], run[4], url)


def textbox(slide, name, l, t, w, h, paras, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT):
    s = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    s.name = name
    set_box(s, paras, anchor, align)
    return s


def by_name(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    print("MISSING", name)
    return None


def kill_prefix(slide, prefix, keep=()):
    n = 0
    for sh in list(slide.shapes):
        if sh.name.startswith(prefix) and sh.name not in keep:
            sh._element.getparent().remove(sh._element)
            n += 1
    print(f"killed {n} prefix {prefix}")


def pic(slide, name, path, l, t, w, h):
    s = slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))
    s.name = name
    s.line.fill.background()
    print("pic", name)
    return s


# ================= S2: Kumbh photo in timeline whitespace =================
s2 = p.slides[1]
for sh in s2.shapes:
    if sh.name == "P2 ev":
        sh.width = Inches(3.3)
print("ev boxes narrowed")
pic(s2, "P2 kumbh", f"{IMG}/kumbh_crowd.jpg", 14.70, 3.90, 3.90, 2.19)
textbox(s2, "P2 kumbhc", 14.70, 6.15, 3.90, 0.90, [
    [("Kumbh mela ground at night, Jan 2025. Photo: Wikimedia Commons.", 11, False, False, GREY)],
])

# ================= S3: machine-view card =================
s3 = p.slides[2]
kill_prefix(s3, "P3 ", keep=("P3 mae",))
textbox(s3, "P3 maet", 1.05, 6.70, 6.90, 0.45,
        [[("What the machine sees", 15, True, False, NAVY)]])
pic(s3, "P3 density", f"{IMG}/jh_fig3_new.png", 1.05, 7.20, 3.00, 2.65)
textbox(s3, "P3 densityc", 1.05, 9.88, 3.00, 0.55, [
    [("Head-density surface from video (Johansson 2008).", 10.5, False, False, GREY)],
])
pic(s3, "P3 flow", f"{IMG}/dis_flow.png", 4.20, 7.20, 3.75, 1.05)
textbox(s3, "P3 flowc", 4.20, 8.30, 3.75, 2.10, [
    [("Flow field on our station clip (DIS optical flow). Movers glow, stillness stays black.", 11, False, False, BODY)],
    [("Counting error on the standard test fell from 68 to 49 MAE as heatmaps improved.", 11, False, False, BODY)],
])
c115 = by_name(s3, "Card 115")
if c115:
    set_box(c115, [
        [("Heatmaps beat boxes", 18, True, False, NAVY)],
        [("At crush density a detector scores F1 0.07 against 0.71 point-based. "
          "Counting error fell from 68 to 49 MAE. (NWPU-Crowd, ShanghaiTech)", 13, False, False, BODY)],
    ])

# ================= S4: pressure strip + deeper calibration =================
s4 = p.slides[3]
kill_prefix(s4, "P4 site")
panel = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.20), Inches(7.45), Inches(9.00), Inches(3.05))
panel.name = "P4 site"
panel.fill.solid()
panel.fill.fore_color.rgb = CARD
panel.line.fill.background()
try:
    panel.adjustments[0] = 0.07
except Exception:
    pass
panel.text_frame.clear()
textbox(s4, "P4 sitet", 10.50, 7.58, 8.40, 0.45,
        [[("Pressure warned first", 16, True, False, NAVY)]])
pic(s4, "P4 pressure", f"{IMG}/pressure_strip.png", 10.50, 8.10, 4.90, 1.89)
textbox(s4, "P4 pressurec", 15.60, 8.10, 3.30, 1.95, [
    [("Pressure crossed the warning line before turbulence began. The accident came after. "
      "Hajj 2006 data (Johansson et al.).", 12, False, False, BODY)],
])
c104 = by_name(s4, "Card 104")
if c104:
    set_box(c104, [
        [("Calibrated where it counts", 20, True, False, NAVY)],
        [("Fixed gates are measured once. Kumbh ran 3-month camera surveys for its crowd alarm. "
          "Other views use relative levels.", 14, False, False, BODY)],
    ])

# ================= S5: venues in Organizers =================
s5 = p.slides[4]
for sh in s5.shapes:
    if sh.name == "Card 104" and sh.has_text_frame and "Organizers" in sh.text_frame.text:
        set_box(sh, [
            [("Organizers", 20, True, False, NAVY)],
            [("Spot a growing jam early, and tell guards which zone to clear. Built for stations, "
              "mela grounds, stadiums.", 15, False, False, BODY)],
        ])
        print("organizers deepened")

# ================= S6: full resource list =================
s6 = p.slides[5]
for nm in ["Card 102", "Card 103", "Card 104", "Card 105"]:
    sh = by_name(s6, nm)
    if sh:
        sh._element.getparent().remove(sh._element)
print("top cards cleared")

cols = [
    ("Count the overlap", [
        ("CSRNet, CVPR 2018", "https://arxiv.org/abs/1802.10062"),
        ("Bayesian Loss, ICCV 2019", "https://arxiv.org/abs/1908.03684"),
        ("DM-Count, NeurIPS 2020", "https://github.com/cvlab-stonybrook/DM-Count"),
        ("P2PNet, ICCV 2021", "https://arxiv.org/abs/2107.12746"),
        ("STEERER / APGCC, 2023-24", "https://arxiv.org/abs/2405.10589"),
        ("Tests: ShanghaiTech, QNRF, NWPU", None),
    ]),
    ("Ground and currents", [
        ("Chan perspective maps, CVPR 2008", "http://www.svcl.ucsd.edu/publications/conference/2008/cvpr08/cvpr08_peoplecnt.pdf"),
        ("Zhang ground-plane fusion, CVPR 2019", "https://openaccess.thecvf.com/content_CVPR_2019/html/Zhang_Wide-Area_Crowd_Counting_via_Ground-Plane_Density_Maps_and_Multi-View_Fusion_CVPR_2019_paper.html"),
        ("PACNN perspective, CVPR 2019", "https://openaccess.thecvf.com/content_CVPR_2019/html/Shi_Revisiting_Perspective_Information_for_Efficient_Crowd_Counting_CVPR_2019_paper.html"),
        ("Mehran social force, CVPR 2009", "https://vision.eecs.ucf.edu/papers/cvpr2009/CVPR09_Mehran.pdf"),
        ("Mehran streaklines, ECCV 2010", "https://www.crcv.ucf.edu/projects/streakline_eccv"),
        ("DIS optical flow (OpenCV)", "https://docs.opencv.org/4.9.0/javadoc/org/opencv/video/DISOpticalFlow.html"),
    ]),
    ("Pressure and risk", [
        ("Helbing social force, 1995", "https://doi.org/10.1103/PhysRevE.51.4282"),
        ("Helbing crowd disasters, 2007", "https://arxiv.org/abs/0708.3339"),
        ("Johansson pressure, 2008", "https://ar5iv.labs.arxiv.org/html/0810.4590"),
        ("Hughes continuum, 2002", "https://doi.org/10.1016/S0191-2615(01)00015-7"),
        ("Nakayama divergence, BMVC 2025", "https://bmvc2025.bmva.org/proceedings/1024"),
        ("Harding early warning, PLoS ONE 2011", "https://arxiv.org/abs/1008.2160"),
    ]),
]
xs = [0.80, 7.00, 13.20]
for (title, rows), x in zip(cols, xs):
    textbox(s6, "R6 colh", x, 3.30, 5.60, 0.42, [[(title, 13, True, False, NAVY)]])
    for i, (txt, url) in enumerate(rows):
        y = 3.78 + i * 0.45
        if url:
            textbox(s6, "R6 row", x, y, 5.60, 0.42, [[(txt, 10.5, False, False, GREY, url)]])
        else:
            textbox(s6, "R6 row", x, y, 5.60, 0.42, [[(txt, 10.5, False, False, GREY)]])
textbox(s6, "R6 build", 0.80, 6.62, 18.40, 0.42, [[
    ("Build from:  ", 10.5, True, False, NAVY),
    ("DM-Count code (MIT)  ", 10.5, False, False, GREY, "https://github.com/cvlab-stonybrook/DM-Count"),
    ("CSRNet model  ", 10.5, False, False, GREY, "https://github.com/leeyeehoo/CSRNet-pytorch"),
    ("homography calibrator  ", 10.5, False, False, GREY, "https://github.com/JuanIsernGhosn/homography-calibrator"),
    ("DeepStream custom-model docs", 10.5, False, False, GREY, "https://docs.nvidia.com/metropolis/deepstream/7.1/text/DS_using_custom_model.html"),
]])

p.save(SRC)
print("saved, new links:", LINKN[0])
