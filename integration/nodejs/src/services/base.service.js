export class BaseService {
  constructor(collectionName) {
    this.collection = null;
    this.collectionName = collectionName;
  }

  async init() {
    const db = await connectToDatabase();
    this.collection = db.collection(this.collectionName);
  }

  async create(document) {
    return this.collection.insertOne(document);
  }

  async find(filter = {}) {
    return this.collection.find(filter).toArray();
  }

  async update(filter, updateDoc) {
    return this.collection.updateOne(filter, { $set: updateDoc });
  }

  async delete(filter) {
    return this.collection.deleteOne(filter);
  }
}
