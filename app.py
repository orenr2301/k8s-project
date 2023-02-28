from flask import Flask, render_template


app = Flask(__name__, template_folder='templates', static_folder='templates')

@app.route('/')
def bg_red():
    return render_template('index.html')

if __name__== "__main__":
    #port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=8080, debug=True)
    
