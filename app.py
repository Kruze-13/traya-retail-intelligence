import os
from flask import Flask, request, jsonify
from data_loader import load_traya_data
from analytics import analyze
from renderer import render

app=Flask(__name__)

def authorized():
    expected=os.getenv('APP_API_KEY','')
    return bool(expected) and request.headers.get('X-API-Key','')==expected

@app.get('/health')
def health(): return jsonify({'ok':True,'service':'traya-email-flash'})

@app.get('/report')
def report():
    if not authorized(): return jsonify({'error':'unauthorized'}),401
    cadence=request.args.get('cadence','weekly').lower()
    if cadence not in ('daily','weekly'): cadence='weekly'
    df,source=load_traya_data(); result=analyze(df,cadence); payload=render(result,cadence); payload['source_file']=source; payload['cadence']=cadence
    return jsonify(payload)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)