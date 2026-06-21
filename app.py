# app.py — our web app
#
# Flask serves pages to the browser. NumPy does fast math.
# Matplotlib draws the spirographs into an image.

import io          # lets us hold an image in memory (no file needed)
import base64      # lets us turn an image into text to send to the browser
from math import gcd

import numpy as np

# Matplotlib normally expects a screen/window. On a web server there's
# no window, so we switch it to "Agg" — a mode that just draws to images.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ---- The spirograph math ----
# Given one dot (position + size + shape), work out the curve's points.
# A spirograph curve is a "hypotrochoid": the path of a pen poked through a
# small circle that rolls around inside a big circle. Three settings:
#   R = big fixed circle, r = small rolling circle (-> petal count),
#   d = pen offset from the rolling circle's centre (-> loopiness).
def spirograph_points(x, y, rx, ry):
    cx, cy = 200, 200          # the canvas circle's centre, in browser pixels
    dx = x - cx
    dy = y - cy
    distance = (dx * dx + dy * dy) ** 0.5      # 0 (centre) .. 180 (edge)
    frac = min(distance / 180.0, 1.0)

    R = 180

    # Petals: position from centre sets the rolling circle size.
    r = int(round(90 - frac * 60))             # 90 down to 30
    if r < 1:
        r = 1

    # Loopiness: the dot's overall SIZE sets the pen offset d.
    size = (rx + ry) / 2.0
    size = max(3.0, min(size, 150.0))
    d = 15 + (size / 150.0) * 115              # ~15 to ~130

    # Stretch: the dot's SHAPE stretches the whole pattern.
    rx = max(rx, 1.0)
    ry = max(ry, 1.0)
    aspect = rx / ry
    x_scale = aspect ** 0.5
    y_scale = 1.0 / x_scale

    # How many full turns until the pattern closes back on itself.
    turns = r // gcd(R, r)
    t = np.linspace(0, 2 * np.pi * turns, 4000)

    xs = ((R - r) * np.cos(t) + d * np.cos((R - r) / r * t)) * x_scale
    ys = ((R - r) * np.sin(t) - d * np.sin((R - r) / r * t)) * y_scale
    return xs, ys


# ---- Draw a whole stack of spirographs onto one image ----
def render_layers(layers):
    fig, ax = plt.subplots(figsize=(5, 5))

    max_extent = 1.0
    for layer in layers:
        xs, ys = spirograph_points(
            layer["x"], layer["y"], layer["rx"], layer["ry"]
        )
        color = layer.get("color", "#e0567a")
        # alpha < 1 makes the line semi-transparent, so layers underneath
        # show through and overlaps blend into richer colours.
        ax.plot(xs, ys, color=color, linewidth=1.2, alpha=0.6)

        # Track how far out the biggest layer reaches, so we can frame it.
        extent = max(np.abs(xs).max(), np.abs(ys).max())
        if extent > max_extent:
            max_extent = extent

    m = max_extent * 1.05
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-m, m)
    ax.set_ylim(-m, m)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode("utf-8")
    return "data:image/png;base64," + encoded


@app.route("/")
def home():
    return render_template("index.html")


# The browser sends the FULL list of layers; we draw them all and reply.
@app.route("/render", methods=["POST"])
def render():
    data = request.get_json()
    layers = data["layers"]
    print(f"Rendering {len(layers)} layer(s)")
    image = render_layers(layers)
    return jsonify({"image": image})


if __name__ == "__main__":
    # Port 5000 is taken by macOS AirPlay, so we use 5001 instead.
    app.run(debug=True, port=5001)
