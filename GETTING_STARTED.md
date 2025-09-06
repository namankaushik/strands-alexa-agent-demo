# Getting Started with Strands Agent Builder

This guide will help you set up Strands Agent Builder with OpenRouter backend for AI-powered conversations.

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- OpenRouter API key

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/namankaushik/strands-alexa-agent-demo.git
cd strands-alexa-agent-demo
```

### 2. Install Dependencies

```bash
npm install
```

or if you prefer yarn:

```bash
yarn install
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory of the project:

```bash
touch .env
```

Add the following environment variables to your `.env` file:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Agent Configuration
AGENT_NAME=Strands Assistant
AGENT_MODEL=openai/gpt-3.5-turbo

# Server Configuration
PORT=3000
NODE_ENV=development
```

### 4. Get Your OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up or log in to your account
3. Navigate to the API section
4. Generate a new API key
5. Copy the API key and replace `your_openrouter_api_key_here` in your `.env` file

### 5. Configure the Agent

Edit the agent configuration file to customize your assistant's behavior:

```javascript
// In config/agent.js or similar
const agentConfig = {
  name: process.env.AGENT_NAME || 'Strands Assistant',
  model: process.env.AGENT_MODEL || 'openai/gpt-3.5-turbo',
  temperature: 0.7,
  maxTokens: 1000,
  systemPrompt: 'You are a helpful AI assistant built with Strands Agent Builder.'
};
```

### 6. Create Launch Script

Create a `start.sh` script for easy launching:

```bash
#!/bin/bash

# Load environment variables
source .env

# Start the Strands Agent Builder
echo "Starting Strands Agent Builder..."
echo "Agent: $AGENT_NAME"
echo "Model: $AGENT_MODEL"
echo "Port: $PORT"

# Run the application
npm start
```

Make the script executable:

```bash
chmod +x start.sh
```

### 7. Launch the Application

Run the launch script:

```bash
./start.sh
```

Or start directly with npm:

```bash
npm start
```

## Verification

Once the application is running, you should see:

1. Server startup messages in the console
2. Confirmation that the OpenRouter connection is established
3. The application running on `http://localhost:3000` (or your configured port)

## Troubleshooting

### Common Issues

**API Key Error**: Ensure your OpenRouter API key is valid and properly set in the `.env` file.

**Port Already in Use**: Change the PORT in your `.env` file to an available port.

**Module Not Found**: Run `npm install` to ensure all dependencies are installed.

**OpenRouter Connection Error**: Check your internet connection and verify the OpenRouter service status.

### Getting Help

If you encounter issues:

1. Check the console logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure your OpenRouter API key has sufficient credits
4. Review the OpenRouter documentation for model-specific requirements

## Next Steps

Once your Strands Agent Builder is running:

1. Test the basic chat functionality
2. Customize the agent's personality and responses
3. Integrate with additional services as needed
4. Deploy to your preferred hosting platform

For more advanced configuration options, refer to the main documentation or explore the configuration files in the project.
