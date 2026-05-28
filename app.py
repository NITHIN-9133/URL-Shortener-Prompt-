from flask import Flask, request, redirect, jsonify, render_template, abort
from database import init_db, shorten_url, get_url, get_all_urls, delete_url
import os

app = Flask(__name__)
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


@app.route("/")
def index():
    urls = get_all_urls()
    return render_template("index.html", urls=urls, base_url=BASE_URL)


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    original_url = data.get("url", "").strip()
    custom_code = data.get("custom_code", "").strip() or None

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url

    result = shorten_url(original_url, custom_code)
    if "error" in result:
        return jsonify(result), 409

    result["short_url"] = f"{BASE_URL}/{result['code']}"
    return jsonify(result), 201


@app.route("/<code>")
def redirect_url(code):
    url = get_url(code)
    if url is None:
        abort(404)
    return redirect(url)


@app.route("/api/urls", methods=["GET"])
def list_urls():
    urls = get_all_urls()
    return jsonify(urls)


@app.route("/api/urls/<code>", methods=["DELETE"])
def remove_url(code):
    deleted = delete_url(code)
    if not deleted:
        return jsonify({"error": "URL not found"}), 404
    return jsonify({"message": f"Deleted /{code}"}), 200


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)