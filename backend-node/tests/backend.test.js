const request = require('supertest');
const app = require('../server');

describe('Backend API Tests', () => {
  
  test('should respond to health check', async () => {
    const res = await request(app)
      .get('/health')
      .expect(200);
    
    expect(res.body).toHaveProperty('status', 'healthy');
    expect(res.body).toHaveProperty('service');
  });
  
  test('should respond to status check', async () => {
    const res = await request(app)
      .get('/status')
      .expect(200);
    
    expect(res.body).toHaveProperty('status', 'running');
    expect(res.body).toHaveProperty('timestamp');
    expect(res.body).toHaveProperty('uptime');
  });
  
  test('should reject signup with missing fields', async () => {
    const res = await request(app)
      .post('/signup')
      .send({
        email: 'test@example.com'
        // Missing password and username
      })
      .expect(400);
    
    expect(res.body).toHaveProperty('error');
  });
  
  test('should reject login with invalid credentials', async () => {
    const res = await request(app)
      .post('/login')
      .send({
        email: 'nonexistent@example.com',
        password: 'wrongpassword'
      })
      .expect(400);
    
    expect(res.body).toHaveProperty('error');
  });
  
});