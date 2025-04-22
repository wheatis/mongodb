Atelier MongoDB - Rapport 
 
Partie 0 - Structure du projet

	atelier-mongodb/
	├── docs/
	│   └── rapport.md          # Documentation principale
	├── mongo/
	│   ├── standalone/         # Config Partie 1
	│   ├── replicaset/         # Config Partie 2
	│   └── sharding/           # Bonus
	├── integration/
	│   └── nodejs/
	│       ├── src/
	│       │   ├── db/
	│       │   │   └── connector.js   	# Gestion de la connexion
	│       │   ├── models/             	# Modèles de données
	│       │   ├── services/           	# Logique métier
	│       │   ├── tests/              	# Tests automatisés
	│       │   └── index.js            	# Point d'entrée
	│       ├── .env.example
	│       └── package.json
	└── README.md               	  	# Instructions globales

Partie 1 - MongoDB Standalone
	
	1. Préparation de l'envirionnement 

		Création du dossier : 
			mkdir -p atelier-mongodb && cd atelier-mongodb

		Création des sous-dossiers : 
			mkdir -p docs mongo/standalone integration/python/tests


	2. Déploiement de MongoDB en mode standalone

		Création du fichier docker-compose dans mongo/standalone/docker-compose.yml
		On utilise la dernière image officielle, on mappe le port 27017 du conteneur sur le même port de la machine hôte, on crée les variables pour créer l’utilisateur administrateur initial et on active l’authentification. 

		On se place ensuite dans le bon dossier et on démarre en arrière plan avec la commande : 
		docker-compose up -d

	3. Création d’un utilisateur administrateur

		On se connecte à MongoDB Shell avec la commande : 
		docker exec -it mongo-standalone mongosh -u admin -p secret --authenticationDatabase admin

		Cela nous permet d'executer la commande dans le conteneur, nous permettant de se connecter avec l'utilisateur root créé automatiquement. 

		Dans le shell MongoDB, je crée un utilisateur monuser sur la base admin : 

		use admin
		db.createUser({
		  user: "monuser",
		  pwd: "monpassword",
		  roles: [ { role: "root", db: "admin" } ]
		});
		
		Capture d'écran (image 2)
		

	4. Création de la base testdb et connexion		

		Etant en groupe et donc sur diffrent OS, nous avons dû installer mongosh sur Kali Linux pour pouvoir travailler correctement, en executant ces commandes : 

		# Créer le dossier pour les clés
		sudo mkdir -p /etc/apt/keyrings

		# Télécharger la clé GPG et la déarmer
		wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | \
		  sudo gpg --dearmor -o /etc/apt/keyrings/mongodb-org-7.0.gpg

		# Ajouter le dépôt MongoDB pour Debian Bookworm (Kali est basé sur Bookworm)
		echo "deb [ signed-by=/etc/apt/keyrings/mongodb-org-7.0.gpg arch=amd64 ] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" \
		  | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

		# Mettre à jour et installer mongosh
		sudo apt update
		sudo apt install -y mongodb-mongosh
		
		Pour se connecter ensuite à testdb, on execute : 
		mongosh "mongodb://monuser:monpassword@localhost:27017/testdb?authSource=admin"

		(ou bien depuis le conteneur : 
		docker exec -it mongo-standalone \
  			mongosh "mongodb://monuser:monpassword@localhost:27017/testdb?authSource=admin")

	5. Vérification via CLI et Compass

		Connexion avec mongosh :
		mongosh "mongodb://monuser:monpassword@localhost:27017/testdb?authSource=admin"

		CRUD sur la base testdb : 
		use testdb
		db.createCollection("utilisateurs")
		db.utilisateurs.insertMany([ { nom: "Alice", age: 28 }, { nom: "Bob", age: 34 } ])
		db.utilisateurs.find()
		db.utilisateurs.updateOne({ nom: "Alice" }, { $set: { age: 29 } })
		db.utilisateurs.deleteOne({ nom: "Bob" })
		
		On s'est amusé a testé les commandes (image 3)

	6. Vérification via CLI et GUI

	CLI : utilisation de mongosh.
	GUI : MongoDB Compass connecté avec l’URI mongodb://monuser:monpassword@localhost:27017/testdb?authSource=admin

Partie 2 - MongoDB Replica Set

	1. Créer la structure du dossier

		cd ~/Ynov/atelier-mongodb/mongo/
		mkdir replicaset
		cd replicaset
		
	2. Créer un fichier docker-compose.yml
		nano docker-compose.yml

		On y met les 3 services mongo1, mongo2 et mongo3, Même replSet appelé rs0, Et chacun a un port différent pour qu'on puisse les contacter.

	3. Lancement des conteneurs 
		docker compose up -d (image 4)

	4. Initialiser le Replica Set
		On rentre dans le conteneur mongo1 et on le configure : 
		docker exec -it mongo1 mongosh
		rs.initiate({

		  _id: "rs0",
		  members: [
		    { _id: 0, host: "mongo1:27017" },
		    { _id: 1, host: "mongo2:27017" },
		    { _id: 2, host: "mongo3:27017" }
		  ]
		})


		Et on vérifie avec rs.status() (image 7)
		Le status de mongo1 est en PRIMARY et celui de mong02 et mongo3 en SECONDARY. 
		Nous allons à présent écrire sur le PRIMARY, et voir si le replica sur les 2 SECONDARY fonctionne bien. 

	5. Ecriture sur le PRIMARY 
		Sur mongo1 : 

		use testdb
		db.testcoll.insertOne({message: "Hello from PRIMARY"})

	6. Lecture sur les SECONDARY 
		Sur mongo2 et mongo3 : 
		docker exec -it mongo2 mongosh 
		puis dans un second temps 
		docker exec -it mongo3 mongosh

		rs.secondaryOk()  // Autorise la lecture sur SECONDARY
		db.testcoll.find()

		Le replica a coorectement fonctionné (image 6)

	7. Configurations 
		L'URI de connexion pour les applications :
		mongodb://mongo1:27017,mongo2:27017,mongo3:27017/testdb?replicaSet=rs0

Partie 3 - Intégration dans une application

	0. Technologies utilisé 
		1. Node.js car simple à installer et très utilisé dans l'écosystème MongoDB
		2. MongoDB Node Driver (module officiel pour communiquer avec MongoDB)
		3. Dotenv permet de protéger les identifiants de base de données
		
		Nous avons décidé d'utiliser Standalone car + simple, moins couteux et plus facile à maintenir pour les test. 
		
	1. Configuration des fichiers 
		Dans le fichier .env.example, les lignes :
		authSource=admin : Spécifie où l'utilisateur est stocké (base admin)
		Pour un replica set : MONGO_HOST=mongo1:27017,mongo2:27018,mongo3:27019&replicaSet=rs0
		
		Dans le fichier src/db/connector.js (code de connexion), les lignes : 
		encodeURIComponent : Encode le mot de passe pour les caractères spéciaux
		MongoClient : Classe principale du driver MongoDB
		useUnifiedTopology : Active le nouveau système de découverte des serveurs
		Le singleton (client) évite de multiples connexions
		
		Dans le fichier src/index.js (code principal CRUD), on retrouve les lignes :
		Insertion : insertOne() pour ajouter 1 document
		Recherche : find() avec filtre (> 25 ans) + toArray() pour conversion
		Mise à jour : updateOne() avec $set pour modifier un champ
		Suppression : deleteOne() avec l'ID du document
		
	2. Modification des fichiers 
		mongo/standalone/docker-compose.yml contient la configuration MongoDB avec authentification
		integration/nodejs/.env contient l'url de connexion 
		integration/nodejs/src/db/connector.js contient la gestion de la connexion sécurisée avec vérifications
		integration/nodejs/src/index.js contient l'implémentation des opérations CRUD avec commentaires
		package.json contient "type": "module" + dépendances (mongodb, dotenv)
	
	3. Information complémentaire 
		Connexion sécurisé avec const uri = process.env.MONGO_URI;
		Méthode de connexion avec Standalone const standaloneURI = 'mongodb://localhost:27017/db'
	
	4. Execution et tests
		On lance l'application avec : 
		cp .env.example .env  # Après avoir choisi les valeurs 
		node src/index.js  
		
	5. Execution réussie 
		On se connecte à la base de données, un document y est inséré et on le repère.
		Ensuite, on le modifie et on le supprime. 
		Les logs sont affichés afin d'avoir un suivi (image 8)
	
		
		
Commentaires libres : 

	La mise en place du projet, surtout au début était plutôt simple et amusante. 
	Les problèmes sérieux sont arrivés lors de la partie 3 à l'intégration de l'application.
	Il était facile de se perdre sur les différents chemins et la configuration des fichiers. 
	La partie bonus n'a pas été faite, manque de temps. 
