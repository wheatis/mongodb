// Produits achetés par Alice
MATCH (c:Client {nom: "Alice"})-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p:Produit)
RETURN p.nom;

// Clients ayant acheté "Clavier"
MATCH (p:Produit {nom: "Clavier"})<-[:CONTIENT]-(:Commande)<-[:A_EFFECTUE]-(c:Client)
RETURN c.nom;

// Commandes contenant "Souris"
MATCH (p:Produit {nom: "Souris"})<-[:CONTIENT]-(com:Commande)
RETURN com.id;

// Suggestions de produits pour un client (produits achetés par d'autres clients ayant acheté les mêmes produits)
MATCH (c1:Client {nom: "Alice"})-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(p:Produit)
MATCH (p)<-[:CONTIENT]-(:Commande)<-[:A_EFFECTUE]-(c2:Client)
WHERE c1 <> c2
MATCH (c2)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(sugg:Produit)
WHERE NOT EXISTS {
    MATCH (c1)-[:A_EFFECTUE]->(:Commande)-[:CONTIENT]->(sugg)
}
RETURN DISTINCT sugg.nom
