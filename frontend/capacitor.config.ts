import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.xgimi.cs.chatbot',
  appName: '极米智能售后助手',
  webDir: 'dist',
  server: {
    // For development: let it connect to a local dev server
    // For production: bundle assets inside APK, API calls go to remote server
    cleartext: true,  // Allow HTTP in development
  },
  // Android-specific settings
  android: {
    allowMixedContent: true,
    captureInput: true,
    webContentsDebuggingEnabled: false,
  },
};

export default config;
