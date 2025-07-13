import React, { useState, useEffect } from 'react';
import { useAuth } from './Auth/AuthContext.jsx';
import { 
  FaUser, 
  FaPalette, 
  FaEye, 
  FaFont, 
  FaMoon, 
  FaSun,
  FaCog,
  FaSave,
  FaBell
} from 'react-icons/fa';

const Settings = () => {
  const { user, authFetch } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    theme: 'dark',
    readingDirection: 'ltr',
    defaultViewMode: 'grid',
    autoHideUI: false,
    nightMode: true,
    fontSize: 16,
    layoutPreference: 'vertical',
    accentColor: '#3B82F6',
    notifications: {
      newChapters: true,
      updates: true,
      recommendations: true
    }
  });

  useEffect(() => {
    fetchUserSettings();
  }, []);

  const fetchUserSettings = async () => {
    try {
      const response = await authFetch('/api/profile');
      if (response.ok) {
        const userData = await response.json();
        if (userData.preferences) {
          setSettings({ ...settings, ...userData.preferences });
        }
      }
    } catch (error) {
      console.error('Failed to fetch user settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const response = await authFetch('/api/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          preferences: settings
        }),
      });

      if (response.ok) {
        // Show success message
        console.log('Settings saved successfully');
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const SettingSection = ({ title, icon: Icon, children }) => (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-center space-x-3 mb-6">
        <Icon className="w-5 h-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      {children}
    </div>
  );

  const SettingItem = ({ label, description, children }) => (
    <div className="flex items-center justify-between py-4 border-b border-gray-700 last:border-b-0">
      <div className="flex-1">
        <label className="text-white font-medium">{label}</label>
        {description && (
          <p className="text-gray-400 text-sm mt-1">{description}</p>
        )}
      </div>
      <div className="ml-4">
        {children}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-1/4 mb-8"></div>
            <div className="space-y-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-800 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
            <p className="text-gray-400">Customize your reading experience</p>
          </div>
          <button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <FaSave className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>

        <div className="space-y-6">
          {/* Appearance Settings */}
          <SettingSection title="Appearance" icon={FaPalette}>
            <div className="space-y-0">
              <SettingItem 
                label="Theme" 
                description="Choose your preferred theme"
              >
                <select
                  value={settings.theme}
                  onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
                  className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                  <option value="auto">Auto</option>
                </select>
              </SettingItem>

              <SettingItem 
                label="Accent Color" 
                description="Choose your accent color"
              >
                <input
                  type="color"
                  value={settings.accentColor}
                  onChange={(e) => setSettings({ ...settings, accentColor: e.target.value })}
                  className="w-12 h-10 bg-gray-700 border border-gray-600 rounded-lg cursor-pointer"
                />
              </SettingItem>

              <SettingItem 
                label="Font Size" 
                description="Adjust the font size for better readability"
              >
                <div className="flex items-center space-x-2">
                  <input
                    type="range"
                    min="12"
                    max="24"
                    value={settings.fontSize}
                    onChange={(e) => setSettings({ ...settings, fontSize: parseInt(e.target.value) })}
                    className="w-24"
                  />
                  <span className="text-white text-sm w-8">{settings.fontSize}px</span>
                </div>
              </SettingItem>
            </div>
          </SettingSection>

          {/* Reading Settings */}
          <SettingSection title="Reading Experience" icon={FaEye}>
            <div className="space-y-0">
              <SettingItem 
                label="Reading Direction" 
                description="Choose how manga pages are displayed"
              >
                <select
                  value={settings.readingDirection}
                  onChange={(e) => setSettings({ ...settings, readingDirection: e.target.value })}
                  className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="ltr">Left to Right</option>
                  <option value="rtl">Right to Left</option>
                  <option value="vertical">Vertical</option>
                </select>
              </SettingItem>

              <SettingItem 
                label="Default View Mode" 
                description="Choose the default layout for manga lists"
              >
                <select
                  value={settings.defaultViewMode}
                  onChange={(e) => setSettings({ ...settings, defaultViewMode: e.target.value })}
                  className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="grid">Grid</option>
                  <option value="list">List</option>
                  <option value="compact">Compact</option>
                </select>
              </SettingItem>

              <SettingItem 
                label="Night Mode" 
                description="Enable dark reading mode for better eye comfort"
              >
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.nightMode}
                    onChange={(e) => setSettings({ ...settings, nightMode: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </SettingItem>

              <SettingItem 
                label="Auto Hide UI" 
                description="Automatically hide the interface while reading"
              >
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.autoHideUI}
                    onChange={(e) => setSettings({ ...settings, autoHideUI: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </SettingItem>
            </div>
          </SettingSection>

          {/* Notification Settings */}
          <SettingSection title="Notifications" icon={FaBell}>
            <div className="space-y-0">
              <SettingItem 
                label="New Chapters" 
                description="Get notified when new chapters are released"
              >
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.newChapters}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {
                        ...settings.notifications,
                        newChapters: e.target.checked
                      }
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </SettingItem>

              <SettingItem 
                label="Updates" 
                description="Get notified about app updates and new features"
              >
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.updates}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {
                        ...settings.notifications,
                        updates: e.target.checked
                      }
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </SettingItem>

              <SettingItem 
                label="Recommendations" 
                description="Get personalized manga recommendations"
              >
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications.recommendations}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {
                        ...settings.notifications,
                        recommendations: e.target.checked
                      }
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </SettingItem>
            </div>
          </SettingSection>
        </div>
      </div>
    </div>
  );
};

export default Settings; 