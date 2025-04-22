import { connect } from './db/connector.js';

async function main() {
  try {
    // 1. Connexion
    const db = await connect();
    const collection = db.collection('users');

    // 2. Insertion
    const insertResult = await collection.insertOne({
      name: 'Jean',
      age: 30,
      email: 'jean@example.com'
    });
    console.log('📥 Document inséré ID:', insertResult.insertedId);

    // 3. Recherche
    const docs = await collection.find({ age: { $gt: 25 } }).toArray();
    console.log('🔍 Résultats recherche:', docs);

    // 4. Mise à jour
    const updateResult = await collection.updateOne(
      { _id: insertResult.insertedId },
      { $set: { age: 31 } }
    );
    console.log('🔄 Documents modifiés:', updateResult.modifiedCount);

    // 5. Suppression
    const deleteResult = await collection.deleteOne({ _id: insertResult.insertedId });
    console.log('🗑️ Documents supprimés:', deleteResult.deletedCount);

  } catch (error) {
    console.error('💥 Erreur:', error);
  }
}

main();