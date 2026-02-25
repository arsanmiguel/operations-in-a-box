#!/usr/bin/env python3
"""
AWS MSP Plugin Manager - Web GUI
===============================

Web-based interface for managing monitoring stack plugins.
Integrates with Grafana for seamless plugin management.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import subprocess
import os
from pathlib import Path
from aws_msp_plugin_manager import PluginManager

app = Flask(__name__)
app.secret_key = 'aws-msp-plugin-manager-secret-key'

# Global plugin manager instance
plugin_manager = None

def init_plugin_manager():
    """Initialize plugin manager with base installation directory"""
    global plugin_manager
    base_dir = Path.cwd() / "customer-monitoring-stack"
    if not base_dir.exists():
        base_dir = Path.cwd()
    plugin_manager = PluginManager(str(base_dir))

@app.route('/')
def index():
    """Main plugin management dashboard"""
    if not plugin_manager:
        init_plugin_manager()
    
    categories = plugin_manager.list_categories()
    installed_plugins = plugin_manager.installed_plugins
    
    # Get plugin stats
    total_plugins = len(plugin_manager.available_plugins)
    installed_count = len(installed_plugins)
    
    return render_template('index.html', 
                         categories=categories,
                         total_plugins=total_plugins,
                         installed_count=installed_count,
                         installed_plugins=installed_plugins)

@app.route('/api/plugins')
def api_plugins():
    """API endpoint to get all plugins"""
    if not plugin_manager:
        init_plugin_manager()
    
    category = request.args.get('category')
    plugins = plugin_manager.list_available_plugins(category)
    
    # Add installation status
    for plugin_id, plugin in plugins.items():
        plugin['installed'] = plugin_id in plugin_manager.installed_plugins
        plugin['id'] = plugin_id
    
    return jsonify(plugins)

@app.route('/api/plugin/<plugin_id>')
def api_plugin_info(plugin_id):
    """API endpoint to get plugin details"""
    if not plugin_manager:
        init_plugin_manager()
    
    plugin = plugin_manager.get_plugin_info(plugin_id)
    if not plugin:
        return jsonify({'error': 'Plugin not found'}), 404
    
    plugin['id'] = plugin_id
    plugin['installed'] = plugin_id in plugin_manager.installed_plugins
    plugin['missing_dependencies'] = plugin_manager.check_dependencies(plugin_id)
    
    return jsonify(plugin)

@app.route('/api/install/<plugin_id>', methods=['POST'])
def api_install_plugin(plugin_id):
    """API endpoint to install a plugin"""
    if not plugin_manager:
        init_plugin_manager()
    
    try:
        force = request.json.get('force', False) if request.json else False
        plugin_manager.install_plugin(plugin_id, force)
        return jsonify({'success': True, 'message': f'Plugin {plugin_id} installed successfully'})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Installation failed: {str(e)}'}), 500

@app.route('/api/uninstall/<plugin_id>', methods=['POST'])
def api_uninstall_plugin(plugin_id):
    """API endpoint to uninstall a plugin"""
    if not plugin_manager:
        init_plugin_manager()
    
    try:
        plugin_manager.uninstall_plugin(plugin_id)
        return jsonify({'success': True, 'message': f'Plugin {plugin_id} uninstalled successfully'})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Uninstallation failed: {str(e)}'}), 500

@app.route('/api/restart-stack', methods=['POST'])
def api_restart_stack():
    """API endpoint to restart the monitoring stack"""
    try:
        # Change to the monitoring stack directory
        base_dir = Path.cwd() / "customer-monitoring-stack"
        if not base_dir.exists():
            base_dir = Path.cwd()
        
        # Restart the stack
        subprocess.run(["docker", "compose", "down"], cwd=base_dir, check=True, capture_output=True)
        subprocess.run(["docker", "compose", "up", "-d"], cwd=base_dir, check=True, capture_output=True)
        
        return jsonify({'success': True, 'message': 'Monitoring stack restarted successfully'})
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': f'Failed to restart stack: {e}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'Restart failed: {str(e)}'}), 500

@app.route('/api/install-pack/<pack_name>', methods=['POST'])
def api_install_pack(pack_name):
    """API endpoint to install plugin packs"""
    if not plugin_manager:
        init_plugin_manager()
    
    packs = {
        'aws-integration': ['aws-cloudwatch', 'aws-discovery', 'cost-optimization'],
        'security-enhancement': ['saml-auth', 'cert-auth'],
        'analytics': ['business-intelligence', 'log-aggregation', 'apm-monitoring'],
        'ai-ml': ['anomaly-detection', 'predictive-alerts'],
        'devops': ['cicd-monitoring', 'gitops-deployment', 'infrastructure-as-code'],
        'enterprise-scale': ['prometheus-federation', 'grafana-ha', 'auto-scaling']
    }
    
    if pack_name not in packs:
        return jsonify({'success': False, 'error': 'Unknown pack'}), 400
    
    try:
        installed = []
        failed = []
        
        for plugin_id in packs[pack_name]:
            try:
                plugin_manager.install_plugin(plugin_id)
                installed.append(plugin_id)
            except Exception as e:
                failed.append({'plugin': plugin_id, 'error': str(e)})
        
        return jsonify({
            'success': len(failed) == 0,
            'installed': installed,
            'failed': failed,
            'message': f'Pack installation completed. {len(installed)} plugins installed, {len(failed)} failed.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Pack installation failed: {str(e)}'}), 500

# HTML Templates (embedded for simplicity)
@app.route('/templates/index.html')
def serve_template():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS MSP Plugin Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #232f3e; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .header p { opacity: 0.8; margin-top: 0.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2rem; font-weight: bold; color: #232f3e; }
        .stat-label { color: #666; margin-top: 0.5rem; }
        .tabs { display: flex; background: white; border-radius: 8px; overflow: hidden; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .tab { flex: 1; padding: 1rem; text-align: center; cursor: pointer; border: none; background: white; }
        .tab.active { background: #232f3e; color: white; }
        .plugin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1rem; }
        .plugin-card { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .plugin-header { display: flex; justify-content: between; align-items: start; margin-bottom: 1rem; }
        .plugin-title { font-size: 1.1rem; font-weight: bold; color: #232f3e; }
        .plugin-category { background: #e3f2fd; color: #1976d2; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .plugin-description { color: #666; margin: 0.5rem 0; }
        .plugin-meta { display: flex; gap: 1rem; margin: 1rem 0; font-size: 0.9rem; color: #666; }
        .plugin-actions { display: flex; gap: 0.5rem; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
        .btn-primary { background: #ff9900; color: white; }
        .btn-secondary { background: #e0e0e0; color: #333; }
        .btn-danger { background: #d32f2f; color: white; }
        .btn:hover { opacity: 0.9; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .installed-badge { background: #4caf50; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
        .packs-section { background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .pack-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
        .pack-card { border: 2px solid #e0e0e0; border-radius: 8px; padding: 1.5rem; cursor: pointer; transition: all 0.2s; }
        .pack-card:hover { border-color: #ff9900; }
        .pack-title { font-weight: bold; color: #232f3e; margin-bottom: 0.5rem; }
        .pack-plugins { color: #666; font-size: 0.9rem; }
        .loading { text-align: center; padding: 2rem; color: #666; }
        .notification { position: fixed; top: 20px; right: 20px; padding: 1rem; border-radius: 4px; color: white; z-index: 1000; }
        .notification.success { background: #4caf50; }
        .notification.error { background: #d32f2f; }
        .restart-banner { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 1rem; border-radius: 4px; margin-bottom: 2rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AWS MSP Plugin Manager</h1>
        <p>Extend your monitoring stack with powerful plugins</p>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-plugins">18</div>
                <div class="stat-label">Available Plugins</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="installed-plugins">0</div>
                <div class="stat-label">Installed Plugins</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">6</div>
                <div class="stat-label">Categories</div>
            </div>
        </div>

        <div id="restart-banner" class="restart-banner" style="display: none;">
            ⚠️ You have installed or uninstalled plugins. 
            <button class="btn btn-primary" onclick="restartStack()">Restart Stack</button> 
            to activate changes.
        </div>

        <div class="packs-section">
            <h2>Popular Plugin Packs</h2>
            <p style="margin-bottom: 1rem; color: #666;">Quick install pre-configured plugin combinations</p>
            <div class="pack-grid">
                <div class="pack-card" onclick="installPack('aws-integration')">
                    <div class="pack-title">AWS Integration Pack</div>
                    <div class="pack-plugins">CloudWatch + Auto-Discovery + Cost Optimization</div>
                </div>
                <div class="pack-card" onclick="installPack('security-enhancement')">
                    <div class="pack-title">Security Enhancement Pack</div>
                    <div class="pack-plugins">SAML Auth + Certificate Auth</div>
                </div>
                <div class="pack-card" onclick="installPack('analytics')">
                    <div class="pack-title">Analytics Pack</div>
                    <div class="pack-plugins">Business Intelligence + ELK + APM</div>
                </div>
                <div class="pack-card" onclick="installPack('ai-ml')">
                    <div class="pack-title">AI/ML Pack</div>
                    <div class="pack-plugins">Anomaly Detection + Predictive Alerts</div>
                </div>
                <div class="pack-card" onclick="installPack('devops')">
                    <div class="pack-title">DevOps Pack</div>
                    <div class="pack-plugins">CI/CD + GitOps + Infrastructure as Code</div>
                </div>
                <div class="pack-card" onclick="installPack('enterprise-scale')">
                    <div class="pack-title">🏢 Enterprise Scale Pack</div>
                    <div class="pack-plugins">Federation + HA + Auto-Scaling</div>
                </div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showCategory('all')">All Plugins</button>
            <button class="tab" onclick="showCategory('Performance & Scale')">Performance</button>
            <button class="tab" onclick="showCategory('Advanced Security')">Security</button>
            <button class="tab" onclick="showCategory('Cloud Integration')">Cloud</button>
            <button class="tab" onclick="showCategory('AI/ML Features')">AI/ML</button>
            <button class="tab" onclick="showCategory('Advanced Analytics')">Analytics</button>
            <button class="tab" onclick="showCategory('DevOps Automation')">DevOps</button>
        </div>

        <div id="plugins-container" class="plugin-grid">
            <div class="loading">Loading plugins...</div>
        </div>
    </div>

    <script>
        let currentCategory = 'all';
        let needsRestart = false;

        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 5000);
        }

        function showRestartBanner() {
            needsRestart = true;
            document.getElementById('restart-banner').style.display = 'block';
        }

        function hideRestartBanner() {
            needsRestart = false;
            document.getElementById('restart-banner').style.display = 'none';
        }

        async function restartStack() {
            try {
                const response = await fetch('/api/restart-stack', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    showNotification('Stack restarted successfully!');
                    hideRestartBanner();
                } else {
                    showNotification(result.error, 'error');
                }
            } catch (error) {
                showNotification('Failed to restart stack', 'error');
            }
        }

        async function installPack(packName) {
            if (!confirm(`Install ${packName} pack? This will install multiple plugins.`)) return;
            
            try {
                const response = await fetch(`/api/install-pack/${packName}`, { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    showNotification(`${packName} pack installed successfully!`);
                    showRestartBanner();
                    loadPlugins();
                } else {
                    showNotification(result.message || result.error, result.success ? 'success' : 'error');
                    if (result.installed && result.installed.length > 0) {
                        showRestartBanner();
                        loadPlugins();
                    }
                }
            } catch (error) {
                showNotification('Failed to install pack', 'error');
            }
        }

        async function installPlugin(pluginId) {
            try {
                const response = await fetch(`/api/install/${pluginId}`, { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const result = await response.json();
                if (result.success) {
                    showNotification(`Plugin ${pluginId} installed!`);
                    showRestartBanner();
                    loadPlugins();
                } else {
                    showNotification(result.error, 'error');
                }
            } catch (error) {
                showNotification('Installation failed', 'error');
            }
        }

        async function uninstallPlugin(pluginId) {
            if (!confirm(`Uninstall ${pluginId}?`)) return;
            
            try {
                const response = await fetch(`/api/uninstall/${pluginId}`, { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    showNotification(`Plugin ${pluginId} uninstalled!`);
                    showRestartBanner();
                    loadPlugins();
                } else {
                    showNotification(result.error, 'error');
                }
            } catch (error) {
                showNotification('Uninstallation failed', 'error');
            }
        }

        function showCategory(category) {
            currentCategory = category;
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            loadPlugins();
        }

        async function loadPlugins() {
            const container = document.getElementById('plugins-container');
            container.innerHTML = '<div class="loading">Loading plugins...</div>';

            try {
                const url = currentCategory === 'all' ? '/api/plugins' : `/api/plugins?category=${encodeURIComponent(currentCategory)}`;
                const response = await fetch(url);
                const plugins = await response.json();

                container.innerHTML = '';
                let installedCount = 0;

                Object.entries(plugins).forEach(([id, plugin]) => {
                    if (plugin.installed) installedCount++;

                    const card = document.createElement('div');
                    card.className = 'plugin-card';
                    card.innerHTML = `
                        <div class="plugin-header">
                            <div>
                                <div class="plugin-title">${plugin.name}</div>
                                <div class="plugin-category">${plugin.category}</div>
                            </div>
                            ${plugin.installed ? '<div class="installed-badge">INSTALLED</div>' : ''}
                        </div>
                        <div class="plugin-description">${plugin.description}</div>
                        <div class="plugin-meta">
                            <span>${plugin.size_mb}MB</span>
                            <span>${plugin.complexity}</span>
                            <span>🔗 ${plugin.dependencies.join(', ')}</span>
                        </div>
                        <div class="plugin-actions">
                            ${plugin.installed 
                                ? `<button class="btn btn-danger" onclick="uninstallPlugin('${id}')">Uninstall</button>`
                                : `<button class="btn btn-primary" onclick="installPlugin('${id}')">Install</button>`
                            }
                            <button class="btn btn-secondary" onclick="showPluginInfo('${id}')">Info</button>
                        </div>
                    `;
                    container.appendChild(card);
                });

                document.getElementById('installed-plugins').textContent = installedCount;
            } catch (error) {
                container.innerHTML = '<div class="loading">Failed to load plugins</div>';
            }
        }

        async function showPluginInfo(pluginId) {
            try {
                const response = await fetch(`/api/plugin/${pluginId}`);
                const plugin = await response.json();
                
                let deps = plugin.missing_dependencies.length > 0 
                    ? `⚠️ Missing: ${plugin.missing_dependencies.join(', ')}`
                    : 'All dependencies satisfied';
                
                alert(`Plugin: ${plugin.name}\\n\\nDescription: ${plugin.description}\\n\\nSize: ${plugin.size_mb}MB\\nComplexity: ${plugin.complexity}\\nServices: ${plugin.docker_services.join(', ')}\\n\\nDependencies: ${deps}`);
            } catch (error) {
                showNotification('Failed to load plugin info', 'error');
            }
        }

        // Load plugins on page load
        loadPlugins();
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    # Check if we're in the right directory
    if not Path('customer-monitoring-stack').exists() and not Path('docker-compose.yml').exists():
        print("Please run this from your monitoring stack directory")
        print("Expected: customer-monitoring-stack/ directory or docker-compose.yml file")
        exit(1)
    
    print("🌐 Starting Plugin Manager Web Interface...")
    print("📱 Access at: http://localhost:5000")
    print("Manage plugins through your browser!")
    print("")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
