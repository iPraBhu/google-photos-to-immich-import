// Google Photos to Immich Import UI

const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    setupTestLogin();
    setupCreateJob();
    setupJobsList();
    loadJobs();
});

function setupTestLogin() {
    const form = document.getElementById('test-login-form');
    const result = document.getElementById('test-result');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            immich_url: document.getElementById('immich-url').value,
            auth_mode: document.getElementById('auth-mode').value,
            api_key: document.getElementById('api-key').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        };
        
        try {
            const response = await fetch(`${API_BASE}/immich/test-login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            document.getElementById('test-result').innerHTML = 
                `<div class="${result.ok ? 'success' : 'error'}">${result.message}</div>`;
        } catch (error) {
            document.getElementById('test-result').innerHTML = 
                `<div class="error">Error: ${error.message}</div>`;
        }
    });
    
    // Toggle auth fields
    const toggleAuthFields = (authModeValue, apiKeyId, emailId, passwordId) => {
        const isApiKey = authModeValue === 'API_KEY';
        document.getElementById(apiKeyId).style.display = isApiKey ? 'block' : 'none';
        document.getElementById(emailId).style.display = isApiKey ? 'none' : 'block';
        document.getElementById(passwordId).style.display = isApiKey ? 'none' : 'block';
    };
    
    document.getElementById('auth-mode').addEventListener('change', (e) => {
        toggleAuthFields(e.target.value, 'api-key', 'email', 'password');
    });
    
    // Set initial state
    toggleAuthFields('API_KEY', 'api-key', 'email', 'password');
}

function setupCreateJob() {
    const form = document.getElementById('create-job-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            immich_url: document.getElementById('job-immich-url').value,
            auth_mode: document.getElementById('job-auth-mode').value,
            api_key: document.getElementById('job-api-key').value,
            email: document.getElementById('job-email').value,
            password: document.getElementById('job-password').value,
            album_links: document.getElementById('album-links').value.split('\n').filter(l => l.trim()),
            create_album: document.getElementById('create-album').checked,
            skip_duplicates: document.getElementById('skip-duplicates').checked,
            store_staging: document.getElementById('store-staging').checked,
            download_concurrency: parseInt(document.getElementById('download-concurrency').value),
            upload_concurrency: parseInt(document.getElementById('upload-concurrency').value)
        };
        
        try {
            const response = await fetch(`${API_BASE}/jobs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok) {
                alert(`Job created: ${result.id}`);
                loadJobs();
            } else {
                alert(`Error: ${result.detail}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        }
    });
    
    // Toggle auth fields for job form
    const toggleJobAuthFields = (authModeValue) => {
        const isApiKey = authModeValue === 'API_KEY';
        document.getElementById('job-api-key').style.display = isApiKey ? 'block' : 'none';
        document.getElementById('job-email').style.display = isApiKey ? 'none' : 'block';
        document.getElementById('job-password').style.display = isApiKey ? 'none' : 'block';
    };
    
    document.getElementById('job-auth-mode').addEventListener('change', (e) => {
        toggleJobAuthFields(e.target.value);
    });
    
    // Set initial state
    toggleJobAuthFields('API_KEY');
}

function setupJobsList() {
    document.getElementById('refresh-jobs').addEventListener('click', loadJobs);
    document.getElementById('pause-queued').addEventListener('click', pauseQueuedJobs);
    document.getElementById('remove-queued').addEventListener('click', removeQueuedJobs);
}

async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/jobs`);
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error('Failed to load jobs:', error);
    }
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-list');
    container.innerHTML = '';
    
    if (jobs.length === 0) {
        container.innerHTML = '<p>No jobs found.</p>';
        return;
    }
    
    jobs.forEach(job => {
        const jobDiv = document.createElement('div');
        jobDiv.className = 'job-item';
        
        const progress = job.progress ? JSON.parse(job.progress) : {};
        
        jobDiv.innerHTML = `
            <div class="job-header">
                <span class="job-id">${job.id}</span>
                <span class="job-status status-${job.status.toLowerCase()}">${job.status}</span>
                <span class="job-created">${new Date(job.created_at).toLocaleString()}</span>
            </div>
            <div class="job-details">
                <div>Immich URL: ${job.immich_url}</div>
                <div>Progress: ${progress.albums_processed || 0}/${progress.total_albums || 0} albums, ${progress.items_processed || 0}/${progress.total_items || 0} items</div>
                ${job.last_error ? `<div class="error">Error: ${job.last_error}</div>` : ''}
                ${job.log_tail ? `<div class="log">Log: ${job.log_tail.replace(/\n/g, '<br>')}</div>` : ''}
            </div>
            <div class="job-actions">
                ${job.status === 'QUEUED' || job.status === 'RUNNING' ? `<button onclick="cancelJob('${job.id}')">Cancel</button>` : ''}
                ${job.status === 'PAUSED' ? `<button onclick="resumeJob('${job.id}')">Resume</button>` : ''}
                ${job.status !== 'RUNNING' ? `<button onclick="deleteJob('${job.id}')" class="delete">Delete</button>` : ''}
            </div>
        `;
        
        container.appendChild(jobDiv);
    });
}

async function cancelJob(jobId) {
    if (!confirm('Are you sure you want to cancel this job?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/cancel`, { method: 'PUT' });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadJobs();
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, { method: 'DELETE' });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadJobs();
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function pauseQueuedJobs() {
    if (!confirm('Are you sure you want to pause all queued jobs?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/jobs/pause-queued`, { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadJobs();
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function removeQueuedJobs() {
    if (!confirm('Are you sure you want to remove all queued jobs? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`${API_BASE}/jobs/remove-queued`, { method: 'DELETE' });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadJobs();
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function resumeJob(jobId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/resume`, { method: 'PUT' });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadJobs();
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}