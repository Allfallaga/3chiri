from app import app

if __name__ == "__main__":
    # Configurer le mode débogage en fonction de l'environnement
    app.run(host="0.0.0.0", port=5000, debug=True)
