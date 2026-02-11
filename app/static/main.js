import { h, render, Component } from 'https://unpkg.com/preact@10.19.2/dist/preact.module.js';

class App extends Component {
  state = {
    // Login state
    isLoggedIn: false,
    loginInfo: null,
    immichUrl: 'http://localhost:2283',
    authMode: 'API_KEY',
    apiKey: '',
    email: '',
    password: '',
    testLoginResult: null,
    testingLogin: false,
    // Import job state
    albumLinks: '',
    options: {
      createAlbum: true,
      skipDuplicates: true,
      downloadConcurrency: 3,
      uploadConcurrency: 3,
      storeStaging: true
    },
    jobs: [],
    loading: false,
    error: null
  };

  componentDidMount() {
    // Load saved login from localStorage
    const saved = localStorage.getItem('immichLogin');
    if (saved) {
      try {
        const loginInfo = JSON.parse(saved);
        this.setState({ isLoggedIn: true, loginInfo });
      } catch (e) {
        console.error('Failed to parse saved login:', e);
      }
    }
    this.loadJobs();
    this.pollInterval = setInterval(() => this.loadJobs(), 5000);
  }

  componentWillUnmount() {
    if (this.pollInterval) clearInterval(this.pollInterval);
  }

  loadJobs = async () => {
    try {
      const r = await fetch('/api/jobs');
      if (r.ok) {
        const jobs = await r.json();
        this.setState({ jobs });
      }
    } catch (e) {
      console.error('Failed to load jobs:', e);
    }
  };

  handleInput = e => {
    const { name, value, type, checked } = e.target;
    if (name in this.state.options) {
      this.setState({ options: { ...this.state.options, [name]: type === 'checkbox' ? checked : value } });
    } else {
      this.setState({ [name]: value });
    }
  };

  handleAuthMode = e => {
    this.setState({ authMode: e.target.value });
  };

  testLogin = async e => {
    e.preventDefault();
    this.setState({ testLoginResult: null, testingLogin: true });
    try {
      const loginData = {
        immich_url: this.state.immichUrl,
        auth_mode: this.state.authMode
      };
      
      if (this.state.authMode === 'API_KEY') {
        loginData.api_key = this.state.apiKey;
      } else {
        loginData.email = this.state.email;
        loginData.password = this.state.password;
      }

      const r = await fetch('/api/immich/test-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      const data = await r.json();
      
      if (data.ok) {
        // Save login info
        const loginInfo = {
          immichUrl: this.state.immichUrl,
          authMode: this.state.authMode,
          apiKey: this.state.authMode === 'API_KEY' ? this.state.apiKey : null,
          email: this.state.authMode === 'CREDENTIALS' ? this.state.email : null,
          password: this.state.authMode === 'CREDENTIALS' ? this.state.password : null,
          user: data.user
        };
        localStorage.setItem('immichLogin', JSON.stringify(loginInfo));
        this.setState({ 
          testLoginResult: data, 
          testingLogin: false,
          isLoggedIn: true,
          loginInfo 
        });
      } else {
        this.setState({ testLoginResult: data, testingLogin: false });
      }
    } catch (e) {
      this.setState({ 
        testLoginResult: { ok: false, message: `Error: ${e.message}` }, 
        testingLogin: false 
      });
    }
  };

  logout = () => {
    localStorage.removeItem('immichLogin');
    this.setState({ 
      isLoggedIn: false, 
      loginInfo: null,
      testLoginResult: null,
      apiKey: '',
      email: '',
      password: ''
    });
  };

  startJob = async e => {
    e.preventDefault();
    this.setState({ loading: true, error: null });
    const { loginInfo } = this.state;
    
    const body = {
      immich_url: loginInfo.immichUrl,
      album_links: this.state.albumLinks.split('\n').filter(l => l.trim()),
      create_album: this.state.options.createAlbum,
      skip_duplicates: this.state.options.skipDuplicates,
      download_concurrency: this.state.options.downloadConcurrency,
      upload_concurrency: this.state.options.uploadConcurrency,
      store_staging: this.state.options.storeStaging
    };
    
    if (loginInfo.authMode === 'API_KEY') {
      body.api_key = loginInfo.apiKey;
    } else {
      body.email = loginInfo.email;
      body.password = loginInfo.password;
    }
    
    try {
      const r = await fetch('/api/jobs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!r.ok) {
        const err = await r.json();
        this.setState({ error: err.detail || 'Failed to create job', loading: false });
        return;
      }
      const data = await r.json();
      this.setState({ 
        jobs: [data, ...this.state.jobs], 
        loading: false,
        albumLinks: '',
        error: null
      });
      await this.loadJobs();
    } catch (e) {
      this.setState({ error: `Error: ${e.message}`, loading: false });
    }
  };

  render(_, s) {
    return h('div', { class: 'modern-container' }, [
      // Hero Section
      h('div', { class: 'hero-section' }, [
        h('h1', { class: 'hero-title' }, '📸 Google Photos → Immich'),
        h('p', { class: 'hero-subtitle' }, 'Seamlessly migrate your Google Photos albums to Immich with metadata preservation'),
        h('div', { class: 'hero-badges' }, [
          h('div', { class: 'badge' }, ['✨', 'Free & Open Source']),
          h('div', { class: 'badge' }, ['🔒', 'Secure & Private']),
          h('div', { class: 'badge' }, ['⚡', 'Fast Import'])
        ])
      ]),

      // Login Section (if not logged in)
      !s.isLoggedIn && h('div', { class: 'glass-card' }, [
        h('div', { class: 'card-header' }, [
          h('div', { class: 'card-icon' }, '🔐'),
          h('div', { class: 'card-title' }, 'Connect to Immich')
        ]),
        h('form', { class: 'modern-form', onSubmit: this.testLogin }, [
          // Immich Server URL
          h('div', { class: 'form-group' }, [
            h('label', {}, 'Immich Server URL'),
            h('div', { class: 'input-wrapper' }, [
              h('span', { class: 'input-icon' }, '🌐'),
              h('input', { 
                name: 'immichUrl', 
                value: s.immichUrl, 
                onInput: this.handleInput, 
                required: true, 
                placeholder: 'http://localhost:2283' 
              })
            ]),
            h('div', { class: 'helper-text' }, 'Enter the full URL of your Immich server')
          ]),

          // Auth Method
          h('div', { class: 'form-group' }, [
            h('label', {}, 'Authentication Method'),
            h('div', { class: 'input-wrapper' }, [
              h('span', { class: 'input-icon' }, '🔐'),
              h('select', { value: s.authMode, onInput: this.handleAuthMode }, [
                h('option', { value: 'API_KEY' }, 'API Key (Recommended)'),
                h('option', { value: 'CREDENTIALS' }, 'Email + Password')
              ])
            ]),
            h('div', { class: 'helper-text' }, 'API Key is more secure and recommended')
          ]),

          // API Key
          s.authMode === 'API_KEY' && h('div', { class: 'form-group' }, [
            h('label', {}, 'Immich API Key'),
            h('div', { class: 'input-wrapper' }, [
              h('span', { class: 'input-icon' }, '🔑'),
              h('input', { 
                name: 'apiKey', 
                value: s.apiKey, 
                onInput: this.handleInput, 
                placeholder: 'Paste your API key here', 
                required: true,
                type: 'password'
              })
            ]),
            h('div', { class: 'helper-text' }, 'Generate in Immich: Settings → Account → API Keys')
          ]),

          // Email/Password
          s.authMode === 'CREDENTIALS' && [
            h('div', { class: 'form-group' }, [
              h('label', {}, 'Email Address'),
              h('div', { class: 'input-wrapper' }, [
                h('span', { class: 'input-icon' }, '✉️'),
                h('input', { 
                  name: 'email', 
                  value: s.email, 
                  onInput: this.handleInput, 
                  placeholder: 'your@email.com', 
                  required: true,
                  type: 'email'
                })
              ])
            ]),
            h('div', { class: 'form-group' }, [
              h('label', {}, 'Password'),
              h('div', { class: 'input-wrapper' }, [
                h('span', { class: 'input-icon' }, '🔒'),
                h('input', { 
                  name: 'password', 
                  value: s.password, 
                  onInput: this.handleInput, 
                  placeholder: 'Your password', 
                  type: 'password', 
                  required: true 
                })
              ])
            ])
          ],

          // Test Login Button
          h('button', { 
            type: 'submit', 
            disabled: s.testingLogin, 
            class: 'btn-primary' 
          }, s.testingLogin ? ['🔄 Connecting...', h('span', { class: 'spinner' })] : '🔐 Login to Immich'),
          
          s.testLoginResult && h('div', { 
            class: s.testLoginResult.ok ? 'success-msg' : 'error-msg' 
          }, s.testLoginResult.message)
        ])
      ]),

      // Logged In Status (if logged in)
      s.isLoggedIn && h('div', { class: 'glass-card login-status' }, [
        h('div', { class: 'login-status-content' }, [
          h('div', { class: 'login-status-icon' }, '✅'),
          h('div', { class: 'login-status-info' }, [
            h('div', { class: 'login-status-title' }, 'Connected to Immich'),
            h('div', { class: 'login-status-details' }, [
              s.loginInfo.user && h('div', {}, `👤 ${s.loginInfo.user.name || s.loginInfo.user.email}`),
              h('div', {}, `🌐 ${s.loginInfo.immichUrl}`),
              h('div', {}, `🔑 ${s.loginInfo.authMode === 'API_KEY' ? 'API Key' : 'Email/Password'}`)
            ])
          ])
        ]),
        h('button', { onClick: this.logout, class: 'btn-logout' }, '🚪 Logout')
      ]),

      // Import Form Card (only show if logged in)
      s.isLoggedIn && h('div', { class: 'glass-card' }, [
        h('div', { class: 'card-header' }, [
          h('div', { class: 'card-icon' }, '🚀'),
          h('div', { class: 'card-title' }, 'Create New Import')
        ]),
        h('form', { class: 'modern-form', onSubmit: this.startJob }, [
          // Album Links
          h('div', { class: 'form-group' }, [
            h('label', {}, 'Google Photos Album Links'),
            h('textarea', { 
              name: 'albumLinks', 
              value: s.albumLinks, 
              onInput: this.handleInput, 
              rows: 5, 
              required: true,
              placeholder: 'https://photos.app.goo.gl/abc123\nhttps://photos.app.goo.gl/def456\n\nPaste one link per line'
            }),
            h('div', { class: 'helper-text' }, 'Paste public Google Photos album links, one per line')
          ]),

          // Options
          h('div', { class: 'form-group' }, [
            h('label', {}, 'Import Options'),
            h('div', { class: 'options-grid' }, [
              h('div', { 
                class: s.options.createAlbum ? 'option-card active' : 'option-card',
                onClick: () => this.setState({ options: { ...s.options, createAlbum: !s.options.createAlbum }})
              }, [
                h('input', { 
                  type: 'checkbox', 
                  checked: s.options.createAlbum,
                  onChange: (e) => e.stopPropagation()
                }), 
                h('div', { class: 'option-content' }, [
                  h('div', { class: 'option-title' }, 'Create Albums'),
                  h('div', { class: 'option-description' }, 'Recreate Google Photos albums in Immich')
                ])
              ]),
              h('div', { 
                class: s.options.skipDuplicates ? 'option-card active' : 'option-card',
                onClick: () => this.setState({ options: { ...s.options, skipDuplicates: !s.options.skipDuplicates }})
              }, [
                h('input', { 
                  type: 'checkbox', 
                  checked: s.options.skipDuplicates,
                  onChange: (e) => e.stopPropagation()
                }), 
                h('div', { class: 'option-content' }, [
                  h('div', { class: 'option-title' }, 'Skip Duplicates'),
                  h('div', { class: 'option-description' }, 'Detect existing photos by checksum')
                ])
              ]),
              h('div', { 
                class: s.options.storeStaging ? 'option-card active' : 'option-card',
                onClick: () => this.setState({ options: { ...s.options, storeStaging: !s.options.storeStaging }})
              }, [
                h('input', { 
                  type: 'checkbox', 
                  checked: s.options.storeStaging,
                  onChange: (e) => e.stopPropagation()
                }), 
                h('div', { class: 'option-content' }, [
                  h('div', { class: 'option-title' }, 'Keep Files'),
                  h('div', { class: 'option-description' }, 'Store downloads on disk for backup')
                ])
              ])
            ])
          ]),

          // Performance
          h('div', { class: 'form-group' }, [
            h('label', {}, 'Performance Settings'),
            h('div', { class: 'perf-grid' }, [
              h('div', { class: 'perf-card' }, [
                h('div', { class: 'perf-label' }, '⬇️ Download Threads'),
                h('input', { 
                  type: 'number', 
                  name: 'downloadConcurrency', 
                  value: s.options.downloadConcurrency, 
                  min: 1, 
                  max: 10, 
                  onInput: this.handleInput 
                })
              ]),
              h('div', { class: 'perf-card' }, [
                h('div', { class: 'perf-label' }, '⬆️ Upload Threads'),
                h('input', { 
                  type: 'number', 
                  name: 'uploadConcurrency', 
                  value: s.options.uploadConcurrency, 
                  min: 1, 
                  max: 10, 
                  onInput: this.handleInput 
                })
              ])
            ]),
            h('div', { class: 'helper-text' }, 'Higher = faster, but more server load (recommended: 3-5)')
          ]),

          // Submit
          h('button', { 
            type: 'submit', 
            disabled: s.loading, 
            class: 'btn-primary start-btn' 
          }, s.loading ? ['🚀 Starting...', h('span', { class: 'spinner' })] : '🚀 Start Import'),
          s.error && h('div', { class: 'error-msg' }, s.error)
        ])
      ]),

      // Jobs Section
      h('div', { class: 'glass-card' }, [
        h('div', { class: 'card-header' }, [
          h('div', { class: 'card-icon' }, '📁'),
          h('div', { class: 'card-title' }, 'Import Jobs')
        ]),
        h('div', { class: 'jobs-grid' }, 
          s.jobs.length === 0 
            ? h('div', { class: 'empty-state' }, [
                h('div', { class: 'empty-state-icon' }, '📭'),
                h('div', { class: 'empty-state-text' }, 'No jobs yet'),
                h('div', { class: 'empty-state-subtext' }, 'Create your first import to get started!')
              ])
            : s.jobs.map(job => 
                h('div', { class: 'job-card', key: job.id }, [
                  h('div', { class: 'job-header' }, [
                    h('div', { class: 'job-title' }, [
                      '📦',
                      h('span', { class: 'job-id' }, job.id.slice(0, 8))
                    ]),
                    h('span', { 
                      class: `status-badge ${job.status.toLowerCase()}` 
                    }, job.status)
                  ]),
                  h('div', { class: 'job-meta' }, [
                    h('div', { class: 'job-meta-item' }, [
                      '🕐',
                      new Date(job.created_at).toLocaleString()
                    ]),
                    job.progress && h('div', { class: 'job-meta-item' }, [
                      '📊',
                      JSON.stringify(job.progress)
                    ])
                  ]),
                  job.last_error && h('div', { class: 'error-msg' }, job.last_error)
                ])
              )
        )
      ])
    ]);
  }
}

render(h(App), document.getElementById('app'));
