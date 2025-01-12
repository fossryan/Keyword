from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import random  # For generating mock popularity scores
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/keywords', methods=['POST'])
def api_call():
    try:
        # Get the keyword from the form submission
        keyword = request.json.get('keyword', '').strip()

        if not keyword:
            return jsonify({"error": "Keyword is required"}), 400

        keywords = [keyword]

        # Get initial suggestions
        url = f"http://suggestqueries.google.com/complete/search?output=firefox&q={keyword}"
        response = requests.get(url, verify=False)
        try:
            suggestions = json.loads(response.text)
        except json.JSONDecodeError:
            suggestions = [[], []]

        keywords.extend(suggestions[1])

        # Mock popularity scores for each keyword
        suggestions_with_scores = [
            {"keyword": kw, "popularity": random.randint(1, 100)} for kw in keywords
        ]

        # Sort by popularity descending
        suggestions_with_scores.sort(key=lambda x: x['popularity'], reverse=True)

        # Save results to CSV
        df = pd.DataFrame(suggestions_with_scores)
        csv_path = os.path.join('downloads', f'{keyword}_keywords.csv')
        df.to_csv(csv_path, index=False)

        return jsonify({
            "keyword": keyword,
            "suggestions": suggestions_with_scores,
            "csv_path": csv_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download', methods=['GET'])
def download_file():
    file_path = request.args.get('file')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404


if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
