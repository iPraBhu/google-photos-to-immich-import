import { h, render, Component } from 'https://unpkg.com/preact@10.19.2/dist/preact.module.js';

class App extends Component {
  state = {
    immichUrl: '',
    authMode: 'API_KEY',
    apiKey: '',
    email: '',
    password: '',
    testLoginResult: null,
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
    this.setState({ testLoginResult: null, loading: true });
    const r = await fetch('/api/immich/test-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        immich_url: this.state.immichUrl,
        email: this.state.email,
        password: this.state.password
      })
    });
    const data = await r.json();
    this.setState({ testLoginResult: data, loading: false });
  };

  startJob = async e => {
    e.preventDefault();
    this.setState({ loading: true, error: null });
    const body = {
      immich_url: this.state.immichUrl,
      auth: this.state.authMode === 'API_KEY' ? { mode: 'API_KEY', api_key: this.state.apiKey } : { mode: 'CREDENTIALS', email: this.state.email, password: this.state.password },
      album_links: this.state.albumLinks.split('\n').map(s => s.trim()).filter(Boolean),
      options: this.state.options
    };
    const r = await fetch('/api/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!r.ok) {
      this.setState({ error: 'Failed to create job', loading: false });
      return;
    }
    const data = await r.json();
    this.setState({ jobs: [data, ...this.state.jobs], loading: false });
  };

  render(_, s) {
    return h('div', {}, [
      h('h1', {}, 'Google Photos → Immich Import'),
      h('form', { onSubmit: this.startJob }, [
        h('label', {}, 'Immich Server URL'),
        h('input', { name: 'immichUrl', value: s.immichUrl, onInput: this.handleInput, required: true, placeholder: 'http://immich-server:2283' }),
        h('div', {}, [
          h('label', {}, 'Auth Method: '),
          h('select', { value: s.authMode, onInput: this.handleAuthMode }, [
            h('option', { value: 'API_KEY' }, 'API Key'),
            h('option', { value: 'CREDENTIALS' }, 'Email + Password')
          ])
        ]),
        s.authMode === 'API_KEY' && h('input', { name: 'apiKey', value: s.apiKey, onInput: this.handleInput, placeholder: 'Immich API Key', required: true }),
        s.authMode === 'CREDENTIALS' && [
          h('input', { name: 'email', value: s.email, onInput: this.handleInput, placeholder: 'Immich Email', required: true }),
          h('input', { name: 'password', value: s.password, onInput: this.handleInput, placeholder: 'Immich Password', type: 'password', required: true }),
          h('button', { onClick: this.testLogin, disabled: s.loading }, 'Test Login'),
          s.testLoginResult && h('div', { style: { color: s.testLoginResult.ok ? 'green' : 'red' } }, s.testLoginResult.message)
        ],
        h('label', {}, 'Google Photos Album Links (one per line)'),
        h('textarea', { name: 'albumLinks', value: s.albumLinks, onInput: this.handleInput, rows: 4, required: true }),
        h('div', {}, [
          h('label', {}, [h('input', { type: 'checkbox', name: 'createAlbum', checked: s.options.createAlbum, onInput: this.handleInput }), ' Create album if missing']),
          h('label', {}, [h('input', { type: 'checkbox', name: 'skipDuplicates', checked: s.options.skipDuplicates, onInput: this.handleInput }), ' Skip duplicates by checksum']),
          h('label', {}, [h('input', { type: 'checkbox', name: 'storeStaging', checked: s.options.storeStaging, onInput: this.handleInput }), ' Store staging files on disk']),
        ]),
        h('label', {}, 'Download concurrency'),
        h('input', { type: 'number', name: 'downloadConcurrency', value: s.options.downloadConcurrency, min: 1, max: 10, onInput: this.handleInput }),
        h('label', {}, 'Upload concurrency'),
        h('input', { type: 'number', name: 'uploadConcurrency', value: s.options.uploadConcurrency, min: 1, max: 10, onInput: this.handleInput }),
        h('button', { type: 'submit', disabled: s.loading }, s.loading ? 'Starting...' : 'Start Import'),
        s.error && h('div', { style: { color: 'red' } }, s.error)
      ]),
      h('h2', {}, 'Jobs'),
      h('div', {}, s.jobs.map(job => h('div', {}, JSON.stringify(job))))
    ]);
  }
}

render(h(App), document.getElementById('app'));
