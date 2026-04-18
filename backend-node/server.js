const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const { RateLimiterMemory } = require('rate-limiter-flexible');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
app.set('trust proxy', 1);

const allowedOrigins = (process.env.CLIENT_ORIGIN || '')
  .split(',')
  .map(origin => origin.trim())
  .filter(Boolean);

const corsOptions = {
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
      callback(null, true);
      return;
    }

    callback(null, false);
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
};

app.use(cors(corsOptions));
app.options('*', cors(corsOptions));
app.use(express.json({ limit: '10mb' }));

// Helper function to format punishment text
const formatPunishmentText = (punishment) => {
  if (!punishment || typeof punishment !== 'object') return 'Not specified';
  
  const parts = [];
  if (punishment.imprisonment && punishment.imprisonment !== 'not_applicable') {
    parts.push(`Imprisonment: ${punishment.imprisonment}`);
  }
  if (punishment.fine && punishment.fine !== 'not_applicable') {
    parts.push(`Fine: ${punishment.fine}`);
  }
  if (punishment.cognizable && punishment.cognizable !== 'not_applicable') {
    parts.push(`Cognizable: ${punishment.cognizable}`);
  }
  if (punishment.bailable && punishment.bailable !== 'not_applicable') {
    parts.push(`Bailable: ${punishment.bailable}`);
  }
  if (punishment.triable_by && punishment.triable_by !== 'not_applicable') {
    parts.push(`Triable by: ${punishment.triable_by}`);
  }
  
  return parts.length > 0 ? parts.join(', ') : 'Not specified';
};

const datasetPath = path.join(__dirname, '..', 'dataset', 'ipc', 'ipc.json');
let ipcSections = [];
let ipcSectionIndex = new Map();

const loadIpcDataset = () => {
  try {
    // Try multiple possible paths for the dataset
    const possiblePaths = [
      datasetPath,
      path.join(__dirname, 'dataset', 'ipc', 'ipc.json'),
      path.join(process.cwd(), 'dataset', 'ipc', 'ipc.json'),
      '/app/dataset/ipc/ipc.json' // Render deployment path
    ];
    
    let datasetRaw = null;
    let loadedPath = null;
    
    for (const possiblePath of possiblePaths) {
      try {
        if (fs.existsSync(possiblePath)) {
          datasetRaw = fs.readFileSync(possiblePath, 'utf8');
          loadedPath = possiblePath;
          break;
        }
      } catch (e) {
        // Continue to next path
      }
    }
    
    if (!datasetRaw) {
      throw new Error('Could not find IPC dataset file in any expected location');
    }
    
    ipcSections = JSON.parse(datasetRaw);
    ipcSectionIndex = new Map(
      ipcSections.map((section) => [String(section.section_number), section])
    );
    console.log(`Loaded ${ipcSections.length} IPC sections from dataset at ${loadedPath}`);
  } catch (error) {
    console.error('Failed to load IPC dataset in backend:', error.message);
    console.error('Current working directory:', process.cwd());
    console.error('Dataset path attempted:', datasetPath);
    ipcSections = [];
    ipcSectionIndex = new Map();
  }
};

loadIpcDataset();

// Health check endpoint
app.get('/health', (req, res) => {
  const healthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    ipcSectionsLoaded: ipcSections.length,
    aiServiceUrl: process.env.AI_SERVICE_URL || 'http://localhost:8000',
    environment: process.env.NODE_ENV || 'development'
  };
  
  if (ipcSections.length === 0) {
    healthStatus.status = 'warning';
    healthStatus.message = 'IPC sections not loaded properly';
  }
  
  res.json(healthStatus);
});

// Serve static audio files
const audioPath = path.join(__dirname, '../ai-service-python/audio');
console.log('Audio path:', audioPath);
app.use('/audio', express.static(audioPath));

// Rate limiting
const rateLimiter = new RateLimiterMemory({
  points: 100, // 100 requests
  duration: 60, // per 60 seconds
});

// Apply rate limiting middleware
app.use((req, res, next) => {
  rateLimiter.consume(req.ip)
    .then(() => {
      next();
    })
    .catch(() => {
      res.status(429).json({ error: 'Too Many Requests' });
    });
});

// MongoDB connection
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/juris_ai', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => console.error('MongoDB connection error:', err));

// User Schema
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  profession: { type: String, default: 'general' },
  preferredLanguage: { type: String, default: 'english' },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

// Query Schema
const querySchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  query: { type: String, required: true },
  response: { type: String },
  audioData: { type: String }, // Base64 encoded audio data
  language: { type: String, default: 'english' },
  profession: { type: String, default: 'general' },
  persona: { type: String, default: 'general' },
  charges: { type: Array, default: [] },
  matchedSections: { type: Array, default: [] },
  sectionsReferenced: { type: [String], default: [] },
  responsePayload: { type: Object, default: null },
  timestamp: { type: Date, default: Date.now }
});

const Query = mongoose.model('Query', querySchema);

// Middleware to authenticate JWT token
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'supersecret', (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// Health check endpoints
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'JURIS AI Node.js Backend' });
});

app.get('/status', (req, res) => {
  res.json({ 
    status: 'running',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// User registration endpoint
app.post('/signup', async (req, res) => {
  try {
    const { username, email, password, profession, preferredLanguage } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({ $or: [{ email }, { username }] });
    if (existingUser) {
      return res.status(400).json({ error: 'User already exists' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create new user
    const user = new User({
      username,
      email,
      password: hashedPassword,
      profession: profession || 'general',
      preferredLanguage: preferredLanguage || 'english'
    });

    await user.save();

    // Generate JWT token
    const token = jwt.sign(
      { userId: user._id, username: user.username },
      process.env.JWT_SECRET || 'supersecret',
      { expiresIn: '7d' }
    );

    res.status(201).json({
      message: 'User created successfully',
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        profession: user.profession,
        preferredLanguage: user.preferredLanguage
      }
    });
  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// User login endpoint
app.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find user by email
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    // Check password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ error: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user._id, username: user.username },
      process.env.JWT_SECRET || 'supersecret',
      { expiresIn: '7d' }
    );

    res.json({
      message: 'Logged in successfully',
      token,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        profession: user.profession,
        preferredLanguage: user.preferredLanguage
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Chat endpoint - sends query to Python AI service
app.post('/chat', authenticateToken, async (req, res) => {
  try {
    const { query, language, profession, enableVoice } = req.body;
    const userId = req.user.userId;

    // Validate input
    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query cannot be empty' });
    }

    // Get user details for personalization
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Prepare request to Python AI service
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';
    
    // Determine query type (simple heuristic)
    const isScenario = query.toLowerCase().includes('scenario') || 
                      query.toLowerCase().includes('situation') ||
                      query.includes('A man') || query.includes('A woman');
    
    const endpoint = isScenario ? '/predict-charges' : '/rag';
    
    const requestBody = isScenario ? {
      scenario: query,
      language: language || user.preferredLanguage || 'english',
      profession: profession || user.profession || 'general',
      enable_voice: enableVoice || false
    } : {
      query: query,
      language: language || user.preferredLanguage || 'english',
      profession: profession || user.profession || 'general',
      enable_voice: enableVoice || false
    };
    
    const aiResponse = await axios.post(`${aiServiceUrl}${endpoint}`, requestBody, {
      timeout: 120000 // 2 minutes timeout
    });

    // For scenario queries, the AI service now returns complete formatted response
    // For regular queries, use the analysis as-is
    const completeResponse = aiResponse.data.complete_response || aiResponse.data.analysis;

    // Save query to database
    const queryRecord = new Query({
      userId,
      query,
      response: completeResponse,
      audioData: aiResponse.data.audio_path,
      language: language || user.preferredLanguage || 'english',
      profession: profession || user.profession || 'general',
      persona: profession || user.profession || 'general',
      charges: isScenario ? (aiResponse.data.charges || []) : [],
      matchedSections: aiResponse.data.matched_sections || [],
      sectionsReferenced: aiResponse.data.sections_referenced || [],
      responsePayload: aiResponse.data.structured_response || aiResponse.data
    });
    await queryRecord.save();

    res.json(aiResponse.data);
  } catch (error) {
    console.error('Chat error:', error.response?.data || error.message);
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({ error: 'AI service temporarily unavailable' });
    }
    
    res.status(500).json({ 
      error: 'An error occurred while processing your request',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Query history endpoint
app.get('/history', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.userId;
    const limit = parseInt(req.query.limit) || 20;
    const skip = parseInt(req.query.skip) || 0;

    const queries = await Query.find({ userId })
      .sort({ timestamp: -1 })
      .limit(limit)
      .skip(skip);

    res.json(queries);
  } catch (error) {
    console.error('History error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete query history endpoint
app.delete('/history', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.userId;
    
    await Query.deleteMany({ userId });
    
    res.json({ message: 'Query history cleared successfully' });
  } catch (error) {
    console.error('Delete history error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete individual query endpoint
app.delete('/query/:queryId', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.userId;
    const queryId = req.params.queryId;
    
    // Find and delete the query, ensuring it belongs to the user
    const deletedQuery = await Query.findOneAndDelete({ 
      _id: queryId, 
      userId: userId 
    });
    
    if (!deletedQuery) {
      return res.status(404).json({ error: 'Query not found' });
    }
    
    res.json({ message: 'Query deleted successfully' });
  } catch (error) {
    console.error('Delete query error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Generate audio endpoint - proxy to Python AI service
app.post('/generate-audio', authenticateToken, async (req, res) => {
  try {
    const { text, language } = req.body;
    
    // Validate input
    if (!text || text.trim().length === 0) {
      return res.status(400).json({ error: 'Text cannot be empty' });
    }

    // Prepare request to Python AI service
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';
    
    const requestBody = {
      text: text,
      language: language || 'english'
    };
    
    const aiResponse = await axios.post(`${aiServiceUrl}/generate-audio`, requestBody, {
      timeout: 120000 // 2 minutes timeout
    });

    res.json(aiResponse.data);
  } catch (error) {
    console.error('Generate audio error:', error.response?.data || error.message);
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({ error: 'AI service temporarily unavailable' });
    }
    
    res.status(500).json({ 
      error: 'An error occurred while generating audio',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// User profile endpoint
app.get('/user-profile', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.userId;
    const user = await User.findById(userId).select('-password');
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error('Profile error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user profile endpoint
app.put('/user-profile', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.userId;
    const { profession, preferredLanguage } = req.body;

    const user = await User.findByIdAndUpdate(
      userId,
      { profession, preferredLanguage },
      { new: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// IPC section lookup endpoint
app.get('/ipc-section/:section', authenticateToken, async (req, res) => {
  try {
    const sectionNumber = req.params.section;
    const section = ipcSectionIndex.get(String(sectionNumber));

    if (!section) {
      return res.status(404).json({ error: 'IPC section not found' });
    }

    res.json(section);
  } catch (error) {
    console.error('IPC section error:', error.response?.data || error.message);

    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/chat/stream', authenticateToken, async (req, res) => {
  try {
    const { query, language, profession } = req.body;
    const userId = req.user.userId;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query cannot be empty' });
    }

    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://localhost:8000';
    const upstream = await axios({
      method: 'post',
      url: `${aiServiceUrl}/pro/stream`,
      data: {
        query,
        language: language || user.preferredLanguage || 'english',
        profession: profession || user.profession || 'general'
      },
      responseType: 'stream',
      timeout: 120000
    });

    res.setHeader('Content-Type', 'application/x-ndjson');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    let finalPayload = null;
    upstream.data.on('data', (chunk) => {
      const text = chunk.toString('utf8');
      text
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean)
        .forEach((line) => {
          try {
            const parsed = JSON.parse(line);
            if (parsed.type === 'final') {
              finalPayload = parsed.data;
            }
          } catch (streamParseError) {
            console.error('Failed to parse stream chunk:', streamParseError.message);
          }
        });

      res.write(chunk);
    });

    upstream.data.on('end', async () => {
      if (finalPayload) {
        try {
          const queryRecord = new Query({
            userId,
            query,
            response: finalPayload.complete_response || finalPayload.analysis,
            language: language || user.preferredLanguage || 'english',
            profession: profession || user.profession || 'general',
            persona: profession || user.profession || 'general',
            charges: finalPayload.charges || [],
            matchedSections: finalPayload.matched_sections || [],
            sectionsReferenced: finalPayload.sections_referenced || [],
            responsePayload: finalPayload
          });
          await queryRecord.save();
        } catch (saveError) {
          console.error('Failed to save streamed query:', saveError.message);
        }
      }

      res.end();
    });

    upstream.data.on('error', (streamError) => {
      console.error('Streaming error:', streamError.message);
      res.end();
    });
  } catch (error) {
    console.error('Chat streaming error:', error.response?.data || error.message);
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({ error: 'AI service temporarily unavailable' });
    }

    return res.status(500).json({
      error: 'An error occurred while streaming your request',
      details: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

// Get all IPC sections endpoint
app.get('/ipc-sections', async (req, res) => {
  try {
    res.json({ sections: ipcSections, total: ipcSections.length });
  } catch (error) {
    console.error('IPC sections error:', error.response?.data || error.message);

    res.status(500).json({ error: 'Internal server error' });
  }
});

// Related IPC sections endpoint
app.get('/ipc-section/:section/related', async (req, res) => {
  try {
    const sectionNumber = req.params.section;
    const section = ipcSectionIndex.get(String(sectionNumber));

    if (!section) {
      return res.status(404).json({ error: 'IPC section not found' });
    }

    const relatedSections = (section.related_sections || [])
      .map((relatedSectionNumber) => ipcSectionIndex.get(String(relatedSectionNumber)))
      .filter(Boolean);

    res.json({ related_sections: relatedSections });
  } catch (error) {
    console.error('Related IPC sections error:', error.response?.data || error.message);

    res.status(500).json({ error: 'Internal server error' });
  }
});

const frontendBuildPath = path.join(__dirname, 'public');
if (require('fs').existsSync(frontendBuildPath)) {
  app.use(express.static(frontendBuildPath));

  app.get('*', (req, res, next) => {
    if (req.path.startsWith('/audio/')) {
      next();
      return;
    }

    res.sendFile(path.join(frontendBuildPath, 'index.html'));
  });
}

// Start server
const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`JURIS AI Backend Server running on port ${PORT}`);
  });
}

module.exports = app;
