# Deploy to Railway.app (Free)

## Quick Setup Steps:

### 1. **Prepare Your Repository**
```bash
# Make sure all files are committed
git add .
git commit -m "Add Railway deployment config"
git push origin main
```

### 2. **Deploy to Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the `railway.json` config

### 3. **Configure Environment Variables**
In Railway dashboard, add these environment variables:
- `POSTGRES_PASSWORD=your_secure_password`
- `POSTGRES_DB=synthetic_data`
- `POSTGRES_USER=grafana`

### 4. **Access Your Dashboard**
- Railway will provide a URL like: `https://your-app.railway.app`
- Your Grafana will be available at: `https://your-app.railway.app:3000`

## Cost: **FREE** (within $5/month credit)

---

# Alternative: Grafana Cloud (Even Easier)

## Quick Setup Steps:

### 1. **Sign up for Grafana Cloud**
- Go to [grafana.com/products/cloud/](https://grafana.com/products/cloud/)
- Create free account

### 2. **Modify Data Generator**
You'll need to modify `generate_data.py` to send data to Grafana Cloud instead of PostgreSQL:

```python
# Add to requirements.txt
requests

# Modify generate_data.py to use Grafana Cloud API
import requests

def send_to_grafana_cloud(metric_name, value, timestamp):
    url = "https://your-instance.grafana.net/api/prom/push"
    headers = {"Authorization": "Bearer YOUR_API_KEY"}
    data = {
        "metrics": [{
            "name": metric_name,
            "value": value,
            "timestamp": timestamp
        }]
    }
    requests.post(url, json=data, headers=headers)
```

### 3. **Import Your Dashboard**
- Export your dashboard JSON
- Import it into Grafana Cloud

## Cost: **100% FREE** (10,000 metrics, 50GB logs)
