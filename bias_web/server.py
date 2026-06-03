"""커뮤니티 정치 성향 분석 웹 서버 (Flask).

실행:
    pip install -r requirements.txt
    python -m bias_web.server
    # http://localhost:5000
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request, send_from_directory

from . import lexicon
from .analyzer import analyze_all, analyze_community
from .sources import COMMUNITIES

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/communities")
def communities():
    return jsonify([{"id": c["id"], "name": c["name"]} for c in COMMUNITIES])


@app.route("/api/analyze-all")
def api_analyze_all():
    return jsonify(analyze_all())


@app.route("/api/analyze/<community_id>")
def api_analyze_one(community_id: str):
    try:
        return jsonify(analyze_community(community_id))
    except KeyError:
        return jsonify({"error": "unknown community"}), 404


@app.route("/api/analyze-text", methods=["POST"])
def api_analyze_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    return jsonify(lexicon.analyze_text(text))


def main():
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=bool(os.getenv("DEBUG")))


if __name__ == "__main__":
    main()
