import assert from 'assert';
import { connectToDatabase } from '../db/connector.js';
import { BaseService } from '../services/base.service.js';

describe('MongoDB Integration Tests', () => {
  let testService;
  
  before(async () => {
    testService = new BaseService('test_collection');
    await testService.init();
  });

  it('should create and find document', async () => {
    const insertResult = await testService.create({ test: 'value' });
    const docs = await testService.find({ _id: insertResult.insertedId });
    
    assert.strictEqual(docs.length, 1);
    assert.strictEqual(docs[0].test, 'value');
  });
});
