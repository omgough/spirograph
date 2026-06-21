# Spirograph

A little web app for making layered spirograph art. You draw a dot inside a
circle, and the app turns it into a spirograph curve. Draw more dots to stack
up colourful layers, pick a palette inspired by famous paintings, watch each
layer trace itself on, and zoom in to admire the detail.

This was built from scratch as a learning project, so the code is heavily
commented and meant to be readable.

---

## What it can do

- **Draw a dot** — press and drag inside the circle to set a dot's position,
  size, and oval shape.
- **Layer spirographs** — every dot you draw adds a new curve on top of the
  others, building up a composition.
- **Colour palettes** — choose between three palettes (Garden, Mosaic, Waves)
  pulled from reference paintings. Each new layer uses the next colour.
- **Animated drawing** — every layer traces itself onto the canvas line by line.
- **Transparency** — lines are semi-transparent, so overlapping colours blend.
- **Zoom window** — hover over the artwork to magnify any area.
- **Clear** — wipe the canvas and start a fresh piece.

---

## How it works (the big picture)

The app has two halves:

- **Python (Flask)** runs a small web server that serves the page. Run it on
  your own computer and your browser talks to it at `localhost`.
- **The browser (HTML + JavaScript)** does the drawing: it captures your dot,
  calculates the spirograph curve, animates it onto a canvas, and handles the
  palettes and zoom.

> The spirograph maths originally lived in Python (using NumPy + Matplotlib).
> It now runs in JavaScript so the curve can be *animated* smoothly in the
> browser. Python is still used to serve the app, and is the natural place to
> add high-quality image export later.

---

## The maths

A spirograph curve is called a **hypotrochoid**: imagine a small circle rolling
around the inside of a big circle, with a pen poked through the small circle.
There are three "knobs":

- **R** — radius of the big fixed circle (here, `R = 180`).
- **r** — radius of the small rolling circle. Controls the **number of petals**.
- **d** — how far the pen sits from the rolling circle's centre. Controls how
  **loopy** the pattern is.

The curve is traced by varying the angle `t` and plotting:

```
x(t) = [ (R - r) * cos(t) + d * cos(((R - r) / r) * t) ] * xScale
y(t) = [ (R - r) * sin(t) - d * sin(((R - r) / r) * t) ] * yScale
```

for `t` going from `0` to `2 * pi * turns`, where `turns = r / gcd(R, r)`
(this is how many full loops it takes for the pattern to close up neatly).

### How your dot becomes those knobs

The dot you draw has a position `(x, y)`, a horizontal radius `rx`, and a
vertical radius `ry`. They map to the maths like this:

| What you draw                     | Affects | How                                             |
|-----------------------------------|---------|-------------------------------------------------|
| **Distance from the centre**      | `r`     | Further out → smaller `r` → more petals         |
| **Size of the dot**               | `d`     | Bigger dot → bigger `d` → loopier pattern       |
| **Oval shape of the dot**         | stretch | Wide dot → wide pattern; tall dot → tall pattern|

The exact formulas (with `distance` measured from the centre of the circle):

```
frac   = min(distance / 180, 1)
r      = round(90 - 60 * frac)        (kept at 1 or more)

size   = clamp((rx + ry) / 2, 3, 150)
d      = 15 + (size / 150) * 115

aspect = rx / ry
xScale = sqrt(aspect)
yScale = 1 / xScale
```

The curve is sampled at 2000 points, scaled to fit the canvas, and drawn with
semi-transparent lines so layers blend.

---

## Getting started (a workflow for a novice)

You only need to do the install step **once**. After that, running the app is
just two commands.

### 1. One-time setup

You need **Python 3** installed. Then install the three libraries the app uses.
Open the **Terminal** app and run:

```
pip3 install flask numpy matplotlib
```

(Wait until you see "Successfully installed".)

### 2. Start the app

In the Terminal, go into the project folder and start the server:

```
cd ~/src_personal/spirograph
python3 app.py
```

You should see a line like:

```
* Running on http://127.0.0.1:5001
```

Leave this Terminal window open — it's the running app. (To stop it later,
click the Terminal and press `Ctrl + C`.)

### 3. Open it in your browser

Open your web browser and go to:

```
http://localhost:5001
```

That's it — you should see the Spirograph page.

### 4. Make some art

1. **Pick a palette** at the top (Garden, Mosaic, or Waves).
2. **Press and drag** inside the left circle to draw a dot:
   - press where you want it,
   - drag outward to make it bigger (and loopier),
   - drag mostly sideways or up-and-down to stretch the shape.
3. **Release** — the spirograph traces itself onto the "Your artwork" canvas.
4. **Repeat** to layer more curves, each in the next palette colour.
5. **Hover** over the artwork to magnify any area in the Zoom window.
6. **Clear all layers** to start over.

---

## Project structure

```
spirograph/
├── app.py               # The Python web server (Flask)
├── templates/
│   └── index.html       # The whole front-end: page, drawing, maths, animation
├── README.md            # This file
└── .gitignore           # Files git should ignore
```

---

## Troubleshooting

- **"Access denied" / HTTP 403 at the address** — make sure you included the
  port: `http://localhost:5001` (not just `localhost`). On macOS, port 5000 is
  taken by AirPlay, which is why this app uses **5001**.
- **`command not found: python3` or `pip3`** — Python isn't installed (or not on
  your PATH). Install Python 3 from python.org.
- **The page won't load** — check the Terminal running `python3 app.py` is still
  open and shows "Running on ...". If you closed it, start it again (step 2).
- **Changes to the code don't show up** — refresh the browser. For changes to
  `app.py`, the server auto-reloads; if in doubt, stop it (`Ctrl + C`) and run
  `python3 app.py` again.

---

## Ideas for next time

- A side **control panel** with a transparency slider and a shape morph knob
  (circle → square → triangle look).
- **Editing individual layers** — select, recolour, delete, or reorder.
- **Saving / exporting** the finished artwork as an image (a good job for Python).
```
