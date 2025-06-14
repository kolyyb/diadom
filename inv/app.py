# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

# Configuration de la base de données
DB_PATH = "inventaire.db"

def init_db():
    """Initialise la base de données si elle n'existe pas"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            quantite_box INTEGER DEFAULT 0,
            quantite_appartement INTEGER DEFAULT 0
        )
        ''')
        
        # Liste des produits initiale
        produits_initiaux = [
            "Lignes à sang",
            "K7 Ergo Flow",
            "K7 FLOW",
            "Dialyseurs",
            "Dialysats",
            "Sodium",
            "Chlorodydube",
            "Aiguilles à fistules",
            "Rallonges aiguilles",
            "Kits de ponctions",
            "Tuyeau extentions",
            "Y",
            "Seringues 20 ml",
            "Seringues 10 ml"
        ]
        
        # Insertion des produits initiaux
        for produit in produits_initiaux:
            cursor.execute("INSERT OR IGNORE INTO produits (nom, quantite_box, quantite_appartement) VALUES (?, 0, 0)", (produit,))
        
        conn.commit()
        conn.close()

# Initialisation de la BD au démarrage
init_db()

@app.route('/')
def index():
    """Page d'accueil avec liste des produits"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM produits ORDER BY nom")
    produits = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', produits=produits)

@app.route('/ajouter', methods=['POST'])
def ajouter_produit():
    """Ajouter un nouveau produit"""
    nom = request.form.get('nom')
    
    if nom:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("INSERT OR IGNORE INTO produits (nom, quantite_box, quantite_appartement) VALUES (?, 0, 0)", (nom,))
        
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/modifier', methods=['POST'])
def modifier_produit():
    """Modifier les quantités d'un produit"""
    produit_id = request.form.get('id')
    quantite_box = request.form.get('quantite_box', 0)
    quantite_appartement = request.form.get('quantite_appartement', 0)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE produits SET quantite_box = ?, quantite_appartement = ? WHERE id = ?", 
        (quantite_box, quantite_appartement, produit_id)
    )
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/supprimer/<int:produit_id>', methods=['POST'])
def supprimer_produit(produit_id):
    """Supprimer un produit"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM produits WHERE id = ?", (produit_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset_stocks():
    """Remettre tous les stocks à zéro"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE produits SET quantite_box = 0, quantite_appartement = 0")
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/statistiques')
def statistiques():
    """Obtenir les statistiques des stocks"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(quantite_box) as total_box, SUM(quantite_appartement) as total_appartement FROM produits")
    stats = cursor.fetchone()
    
    total_box = stats['total_box'] or 0
    total_appartement = stats['total_appartement'] or 0
    total_general = total_box + total_appartement
    
    conn.close()
    
    return jsonify({
        'total_box': total_box,
        'total_appartement': total_appartement,
        'total_general': total_general
    })

if __name__ == '__main__':
    app.run(debug=True)