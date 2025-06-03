from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
auth = ("neo4j", "password")

data = {
    "clients": ["Alice", "Bob", "Charlie"],
    "produits": ["Ordinateur", "Souris", "Clavier", "Écran"],
    "commandes": [
        {"client": "Alice", "produits": ["Ordinateur", "Souris"]},
        {"client": "Bob", "produits": ["Clavier"]},
        {"client": "Charlie", "produits": ["Écran", "Clavier", "Souris"]},
    ]
}

class GraphApp:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def insert_data(self):
        with self.driver.session() as session:
            # Nettoyage
            session.run("MATCH (n) DETACH DELETE n")

            # Création clients
            for client in data["clients"]:
                session.run("CREATE (:Client {nom: $nom})", nom=client)

            # Création produits
            for produit in data["produits"]:
                session.run("CREATE (:Produit {nom: $nom})", nom=produit)

            # Création commandes
            for i, cmd in enumerate(data["commandes"]):
                client = cmd["client"]
                produits = cmd["produits"]
                cmd_id = f"CMD{i+1}"

                session.run("""
                    MATCH (c:Client {nom: $client})
                    CREATE (com:Commande {id: $cmd_id})
                    CREATE (c)-[:A_EFFECTUE]->(com)
                """, client=client, cmd_id=cmd_id)

                for produit in produits:
                    session.run("""
                        MATCH (com:Commande {id: $cmd_id}), (p:Produit {nom: $produit})
                        CREATE (com)-[:CONTIENT]->(p)
                    """, cmd_id=cmd_id, produit=produit)

app = GraphApp(uri, auth)
app.insert_data()
app.close()
