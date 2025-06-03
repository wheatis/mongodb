from flask import Flask, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

@app.route("/", methods=["GET"])
def index():
    return """
    <h1>API Neo4j - TP</h1>
    <p>Utilise les routes suivantes :</p>
    <ul>
        <li>/produits/&lt;nom_client&gt; — Affiche les produits achetés par le client</li>
        <li>/suggestions/&lt;nom_client&gt; — Suggère des produits</li>
    </ul>
    """

@app.route("/produits/<client>")
def produits_achetes(client):
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Client {nom: $client})-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p:Produit)
            RETURN p.nom AS nom
        """, client=client)
        produits = [record["nom"] for record in result]
        return jsonify(produits)

@app.route("/clients/<produit>")
def clients_ayant_achete(produit):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Produit {nom: $produit})<-[:CONTIENT]-(:Commande)<-[:A_EFFECTUE]-(c:Client)
            RETURN c.nom AS nom
        """, produit=produit)
        clients = [record["nom"] for record in result]
        return jsonify(clients)

@app.route("/commandes_contenant/<produit>")
def commandes_contenant(produit):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Produit {nom: $produit})<-[:CONTIENT]-(com:Commande)
            RETURN com.id AS id
        """, produit=produit)
        commandes = [record["id"] for record in result]
        return jsonify(commandes)

@app.route("/suggestions/<client>")
def suggestions(client):
    with driver.session() as session:
        result = session.run("""
            MATCH (c1:Client {nom: $client})-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p:Produit)
            MATCH (p)<-[:CONTIENT]-(:Commande)<-[:A_EFFECTUE]-(c2:Client)
            WHERE c1 <> c2
            MATCH (c2)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(sugg:Produit)
            WHERE NOT EXISTS {
                MATCH (c1)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(sugg)
            }
            RETURN DISTINCT sugg.nom AS nom
        """, client=client)
        suggestions = [record["nom"] for record in result]
        return jsonify(suggestions)

if __name__ == "__main__":
    app.run(debug=True)
