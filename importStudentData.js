const fs = require('fs');
const { MongoClient } = require('mongodb');

// MongoDB connection string - update this with your MongoDB URI
const uri = 'mongodb://localhost:27017/';
const dbName = 'studentDB';
const collectionName = 'students';

// Path to the JSON file
const dataFilePath = './student_data.json';

async function importData() {
  try {
    // Read and parse the JSON file
    const data = JSON.parse(fs.readFileSync(dataFilePath, 'utf8'));
    
    // Connect to MongoDB
    const client = new MongoClient(uri);
    await client.connect();
    console.log('Connected to MongoDB');
    
    // Check if database exists, create if it doesn't
    const adminDb = client.db('admin');
    const dbList = await adminDb.admin().listDatabases();
    const dbExists = dbList.databases.some(db => db.name === dbName);
    
    if (!dbExists) {
      console.log(`Database '${dbName}' does not exist, creating it...`);
      // In MongoDB, creating a database is implicit when accessing it
    }
    
    const db = client.db(dbName);
    
    // Check if collection exists, create if it doesn't
    const collections = await db.listCollections({name: collectionName}).toArray();
    if (collections.length === 0) {
      console.log(`Collection '${collectionName}' does not exist, creating it...`);
      await db.createCollection(collectionName);
      console.log(`Collection '${collectionName}' created.`);
    }
    
    const collection = db.collection(collectionName);
    
    // Delete existing data (optional)
    await collection.deleteMany({});
    
    // Import the data
    const result = await collection.insertMany(data);
    console.log(`${result.insertedCount} documents were inserted into MongoDB`);
    
    await client.close();
    console.log('Import complete');
  } catch (err) {
    console.error('Error importing data:', err);
  }
}

importData();
