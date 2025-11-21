# EC2 Setup (Amazon Linux 2023) for cs5500-final-backend

This walks through preparing an EC2 host, running Postgres + backend in Docker, and enabling GitHub Actions deploy via SSM. Assumes:
- Amazon Linux 2023 AMI
- `t3.small` (works for demo; monitor memory/CPU credits)
- You already have the repo secrets set (AWS creds, Docker Hub creds, `EC2_INSTANCE_ID`)

## 1) Create/launch EC2
- AMI: Amazon Linux 2023
- Instance: `t3.small`
- Storage: gp3 30–50 GB
- Security group: allow 80/443 for app; 22 only if using SSH; SSM (port 443) allowed by default; block 5432 from public
- IAM role (preferred): or use access key secrets as you have now. Attach SSM managed policy and ECR read if needed later.

## 2) Install Docker on the instance
```bash
sudo dnf update -y
sudo dnf install -y docker docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user  # re-login to use docker without sudo
```

## 3) (Optional) Add swap on t3.small for headroom
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

## 4) Prepare app directory and env
```bash
sudo mkdir -p /opt/classconnect
cd /opt/classconnect
sudo tee .env.prod >/dev/null <<'EOF'
# copy from .env.example.prod and fill real values
APP_NAME=5500 Backend
APP_ENV=prod
PORT=8000
HOST_PORT=8000
DATABASE_URL=postgresql+psycopg://class_connect_user:class_connect_password@database:5432/class_connect_db
POSTGRES_USER=class_connect_user
POSTGRES_PASSWORD=class_connect_password
POSTGRES_DB=class_connect_db
JWT_SECRET=REPLACE_ME_STRONG
JWT_EXPIRE_HOURS=24
CORS_ORIGINS=["https://your-frontend.example.com"]
PUBLIC_APP_URL=https://your-frontend.example.com
LOG_LEVEL=info
MAINTENANCE_ADMIN_PASSWORD=REPLACE_ME_STRONG
SYSTEM_DEFAULT_ACTIVITY_ID=
OPENROUTER_API_KEY=
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_API_BASE=https://openrouter.ai/api/v1/chat/completions
EOF
```

## 5) Ensure SSM is online
Amazon Linux 2023 includes SSM Agent. Verify:
```bash
sudo systemctl status amazon-ssm-agent
```
If not running:
```bash
sudo systemctl enable --now amazon-ssm-agent
```

## 6) (Optional) Manual first-time run/seed
If you want to test before CI:
```bash
cd /opt/classconnect
curl -O https://raw.githubusercontent.com/your-repo/cs5500-final-backend/main/docker-compose.prod.yml
IMAGE_NAME=your-dockerhub-username/cs5500-backend IMAGE_TAG=latest sudo docker compose -f docker-compose.prod.yml up -d database
sudo docker compose -f docker-compose.prod.yml run --rm backend uv run alembic upgrade head
sudo docker compose -f docker-compose.prod.yml run --rm backend uv run python scripts/seed_deploy.py
sudo docker compose -f docker-compose.prod.yml up -d backend
```

## 7) GitHub Actions deploy (already configured in `.github/workflows/deploy.yml`)
What the workflow does on pushes to `main`:
- Builds `Dockerfile`, pushes to Docker Hub as `DOCKER_USERNAME/cs5500-backend:{sha}` and `:latest`
- Sends `docker-compose.prod.yml` to your instance via SSM
- On EC2: pulls image, ensures DB healthy, runs Alembic migrations, seeds with `scripts/seed_deploy.py`, then starts backend

Required repo secrets (already noted in screenshot):
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- `EC2_INSTANCE_ID`

## 8) Verify
```bash
sudo docker compose -f /opt/classconnect/docker-compose.prod.yml ps
curl -I http://<your-ec2-public-dns>/health
```

## 9) Ops tips
- Keep `/opt/classconnect/.env.prod` out of git; edit only on the server or via SSM session
- Enable CloudWatch log shipping if you want centralized logs, or use `docker logs` locally
- Regularly prune old images: `sudo docker image prune -f`
- Back up the Postgres volume (`pgdata`), or snapshot the EBS volume as needed
