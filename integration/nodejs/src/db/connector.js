import { MongoClient } from 'mongodb';
import 'dotenv/config';

export async function connect() {
  if (!process.env.MONGO_URI) {
    console.error('❌ MONGO_URI non définie dans .env');
    process.exit(1);
  }

  try {
    const client = new MongoClient(process.env.MONGO_URI);
    await client.connect();
    console.log('✅ Connecté à MongoDB');
    return client.db();
  } catch (error) {
    console.error('❌ Erreur de connexion :', error.message);
    console.log('URI utilisée :', process.env.MONGO_URI.replace(/:[^@]+@/, ':*****@'));
    process.exit(1);
  }
}
